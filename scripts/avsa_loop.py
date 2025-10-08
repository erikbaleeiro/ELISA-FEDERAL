"""AVSA conversational loop com SmartRouter híbrido.

Executa fluxo "feijão com arroz" entre instruções de voz/texto e agentes
CrewAI placeholders. Agora inclui roteamento automático Gemini/GPU/Claude e
registro estruturado para rodar no backend FastAPI + Render.
"""
from __future__ import annotations

import json
import os
import queue
import threading
import time
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Dict, Iterable, List, Optional


class TaskBacklog:
    def __init__(self) -> None:
        self._size = 0
        self._lock = threading.Lock()

    def push(self) -> None:
        with self._lock:
            self._size += 1

    def complete(self) -> None:
        with self._lock:
            if self._size:
                self._size -= 1

    def size(self) -> int:
        with self._lock:
            return self._size


@dataclass
class AgentSpec:
    name: str
    role: str
    handler: Callable[["TaskRequest"], "TaskResult"]


@dataclass
class TaskRequest:
    instruction: str
    task_type: str = "generic"
    complexity: int = 5
    critical: bool = False
    context_size: int = 0
    media_type: Optional[str] = None
    estimated_seconds: int = 120
    context: Dict[str, str] = field(default_factory=dict)


@dataclass
class TaskResult:
    status: str
    output: str
    artifacts: Dict[str, str] = field(default_factory=dict)


@dataclass
class RoutingDecision:
    model: str
    provider: str
    notes: str


class VoiceIO:
    def __init__(self) -> None:
        self.enabled = bool(os.getenv("GEMINI_LIVE_API_KEY"))

    def listen(self) -> str:
        if not self.enabled:
            return input("🗣️ Instrução (digite ou 'sair'): ")
        # TODO: integrar com Gemini Live streaming
        raise NotImplementedError("Gemini Live ainda não integrado.")

    def speak(self, message: str) -> None:
        if not self.enabled:
            print(f"🔊 {message}")
            return
        # TODO: enviar mensagem sintetizada via Gemini Live
        raise NotImplementedError("Gemini Live ainda não integrado.")


class CrewOrchestrator:
    def __init__(self, agents: Iterable[AgentSpec]) -> None:
        self.agents = list(agents)

    def plan(self, instruction: str) -> List[AgentSpec]:
        ordered: List[AgentSpec] = []
        lower = instruction.lower()
        if any(keyword in lower for keyword in ("plan", "planeja", "roadmap")):
            ordered.append(self._get_agent("planning"))
        if any(keyword in lower for keyword in ("pesquisa", "search", "consult")):
            ordered.append(self._get_agent("search"))
        ordered.append(self._get_agent("coding"))
        ordered.append(self._get_agent("testing"))
        if "refactor" in lower or "refatora" in lower or "corrige" in lower:
            ordered.append(self._get_agent("refactoring"))
        return [agent for agent in ordered if agent]

    def run(self, request: TaskRequest) -> List[TaskResult]:
        plan = self.plan(request.instruction)
        if not plan:
            plan = self.agents
        results: List[TaskResult] = []
        for agent in plan:
            try:
                result = agent.handler(request)
            except Exception as exc:  # noqa: BLE001
                result = TaskResult(status="failed", output=str(exc))
            results.append(result)
            if result.status == "failed":
                break
        return results

    def _get_agent(self, role_token: str) -> Optional[AgentSpec]:
        for agent in self.agents:
            if role_token in agent.role:
                return agent
        return None


def planning_handler(task: TaskRequest) -> TaskResult:
    steps = ["Coletar requisitos", "Validar escopo", "Definir entregas"]
    return TaskResult(status="ok", output=" \n".join(steps))


def search_handler(task: TaskRequest) -> TaskResult:
    query = task.instruction
    return TaskResult(status="ok", output=f"Consulta Haystack: {query}")


def coding_handler(task: TaskRequest) -> TaskResult:
    model = task.context.get("model", "qwen-2.5-coder-32b")
    return TaskResult(status="ok", output=f"{model} gerou código para: {task.instruction}")


def testing_handler(task: TaskRequest) -> TaskResult:
    return TaskResult(status="ok", output="Testes executados (stub)")


def refactoring_handler(task: TaskRequest) -> TaskResult:
    return TaskResult(status="ok", output="Refatoração concluída (stub)")


def build_default_agents() -> List[AgentSpec]:
    return [
        AgentSpec(name="Planner", role="planning", handler=planning_handler),
        AgentSpec(name="Searcher", role="search", handler=search_handler),
        AgentSpec(name="Coder", role="coding", handler=coding_handler),
        AgentSpec(name="Tester", role="testing", handler=testing_handler),
        AgentSpec(name="Refiner", role="refactoring", handler=refactoring_handler),
    ]


def persist_history(log_path: str, record: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


class UsageTracker:
    def __init__(self) -> None:
        self._current_day = date.today()
        self._usage = 0

    def add_usage(self, tokens: int) -> None:
        if date.today() != self._current_day:
            self._current_day = date.today()
            self._usage = 0
        self._usage += max(tokens, 0)

    def get_daily_usage(self) -> int:
        if date.today() != self._current_day:
            self._current_day = date.today()
            self._usage = 0
        return self._usage


class ZeroCostRouter:
    def __init__(self) -> None:
        self.usage_tracker = UsageTracker()

    def route(self, task: TaskRequest) -> str:
        if self._can_run_local(task):
            return self._get_local_model(task)

        if self._can_use_free_tier(task):
            return "gemini-2.0-flash-exp"

        if task.complexity > 9 and task.critical:
            return "claude-sonnet-4.5"

        return "qwen-2.5-coder-32b"

    def route_local(self, task: TaskRequest) -> str:
        return self._get_local_model(task)


class GPUConnector:
    def __init__(self, boot_seconds: int = 30) -> None:
        self.host = os.getenv("GPU_SSH_HOST", "ssh.runpod.io")
        self.port = int(os.getenv("GPU_SSH_PORT", "22"))
        self.user = os.getenv("GPU_SSH_USER", "root")
        self.boot_seconds = boot_seconds
        self.instance_label = os.getenv("GPU_INSTANCE", "RTX-3090")
        self.provider = os.getenv("GPU_PROVIDER", "runpod")
        self._online = False
        self._last_boot = 0.0

    def is_online(self) -> bool:
        return self._online

    def should_boot(self, backlog_size: int, estimated_seconds: int) -> bool:
        if backlog_size >= 5:
            return True
        if estimated_seconds >= 600:
            return True
        return False

    def start_worker(self) -> None:
        self._online = True
        self._last_boot = time.time()

    def stop_worker(self) -> None:
        self._online = False

    def descriptor(self) -> str:
        return f"{self.provider}:{self.instance_label}"


class SmartRouter:
    def __init__(
        self,
        backlog: TaskBacklog,
        local_router: Optional[ZeroCostRouter] = None,
        gpu_connector: Optional[GPUConnector] = None,
    ) -> None:
        self.backlog = backlog
        self.local_router = local_router or ZeroCostRouter()
        self.gpu_connector = gpu_connector or GPUConnector()
        self.usage_tracker = self.local_router.usage_tracker

    def route(self, task: TaskRequest) -> RoutingDecision:
        self.usage_tracker.add_usage(len(task.instruction))
        gpu_label = self.gpu_connector.descriptor()

        if task.complexity <= 4 and not task.critical:
            return RoutingDecision(
                model="gemini-2.0-flash-exp",
                provider="cloud-free",
                notes="Tarefa simples roteada para Gemini Flash (free tier).",
            )

        if task.task_type == "coding" and task.complexity <= 7:
            if self._ensure_gpu(task):
                model = self.local_router.route_local(task)
                return RoutingDecision(
                    model=model,
                    provider="gpu-rental",
                    notes=f"Código médio executado via GPU sob demanda ({gpu_label}).",
                )
            return RoutingDecision(
                model="claude-sonnet-4.5",
                provider="cloud-paid",
                notes="Sem GPU ativa, desviando código médio para Claude.",
            )

    
        if task.task_type == "multimedia":
            if self._ensure_gpu(task):
                local_model = "llava-1.6-34b" if task.media_type == "image" else "whisper-large-v3"
                return RoutingDecision(
                    model=local_model,
                    provider="gpu-rental",
                    notes=f"Multimodal atendido pela GPU local ({gpu_label}).",
                )
            return RoutingDecision(
                model="gpt-4o",
                provider="cloud-paid",
                notes="GPU offline, utilizando GPT-4o para multimodal.",
            )

        if task.complexity >= 9 or task.critical:
            return RoutingDecision(
                model="claude-sonnet-4.5",
                provider="cloud-paid",
                notes="Tarefa crítica/complexa escalada direto para Claude.",
            )

        if self._ensure_gpu(task):
            model = self.local_router.route_local(task)
            return RoutingDecision(
                model=model,
                provider="gpu-rental",
                notes=f"Fallback padrão priorizando modelo local na GPU ({gpu_label}).",
            )

        return RoutingDecision(
            model="claude-sonnet-4.5",
            provider="cloud-paid",
            notes="Fallback final para Claude Sonnet.",
        )

    def _ensure_gpu(self, task: TaskRequest) -> bool:
        if self.gpu_connector.is_online():
            return True
        backlog_size = self.backlog.size()
        if self.gpu_connector.should_boot(backlog_size, task.estimated_seconds):
            self.gpu_connector.start_worker()
            time.sleep(min(self.gpu_connector.boot_seconds, 3))
            return True
        return False

    def _can_run_local(self, task: TaskRequest) -> bool:
        if task.task_type == "planning" and task.complexity <= 8:
            return True
        if task.task_type == "coding":
            return True
        if task.task_type == "multimedia":
            return True
        if task.context_size and task.context_size < 128_000:
            return True
        return False

    def _get_local_model(self, task: TaskRequest) -> str:
        if task.task_type == "coding":
            if task.complexity >= 7:
                return "qwen-2.5-coder-32b"
            return "deepseek-coder-v2-lite-16b"
        if task.task_type == "multimedia":
            if task.media_type == "image":
                return "llava-1.6-34b"
            if task.media_type == "audio":
                return "whisper-large-v3"
        return "qwen-2.5-coder-32b"

    def _can_use_free_tier(self, task: TaskRequest) -> bool:
        daily_usage = self.usage_tracker.get_daily_usage()
        if daily_usage < 1_000_000 and not task.critical:
            return True
        return False


def estimate_duration(task_type: str, complexity: int) -> int:
    base = {
        "planning": 240,
        "coding": 420,
        "testing": 300,
        "multimedia": 260,
        "generic": 240,
    }.get(task_type, 240)
    adjustment = (complexity - 5) * 45
    return max(90, base + adjustment)


def infer_task_profile(instruction: str) -> Dict[str, object]:
    lowered = instruction.lower()
    profile: Dict[str, object] = {
        "task_type": "generic",
        "complexity": 5,
        "critical": "crit" in lowered or "urgente" in lowered,
        "context_size": 0,
        "media_type": None,
        "estimated_seconds": 180,
    }

    if any(word in lowered for word in ("planeja", "plan", "roadmap")):
        profile["task_type"] = "planning"
        profile["complexity"] = 6
    elif any(word in lowered for word in ("cod", "implementar", "construir")):
        profile["task_type"] = "coding"
        profile["complexity"] = 7
    elif any(word in lowered for word in ("test", "validar", "qa")):
        profile["task_type"] = "testing"
        profile["complexity"] = 5
    elif any(word in lowered for word in ("imagem", "foto", "ocr")):
        profile["task_type"] = "multimedia"
        profile["media_type"] = "image"
    elif any(word in lowered for word in ("áudio", "voz", "transcre")):
        profile["task_type"] = "multimedia"
        profile["media_type"] = "audio"

    if any(word in lowered for word in ("complexo", "difícil", "avançado")):
        profile["complexity"] = max(profile["complexity"], 8)
    if any(word in lowered for word in ("simples", "básico", "feijão")):
        profile["complexity"] = min(profile["complexity"], 4)

    profile["estimated_seconds"] = estimate_duration(
        profile["task_type"], profile["complexity"]
    )

    return profile


def main() -> None:
    voice = VoiceIO()
    orchestrator = CrewOrchestrator(build_default_agents())
    backlog = TaskBacklog()
    smart_router = SmartRouter(backlog=backlog)
    feedback_queue: "queue.Queue[str]" = queue.Queue()

    def announcer() -> None:
        while True:
            message = feedback_queue.get()
            if message is None:
                break
            voice.speak(message)

    announcer_thread = threading.Thread(target=announcer, daemon=True)
    announcer_thread.start()

    log_file = os.path.join("logs", "avsa_history.log")

    while True:
        instruction = voice.listen().strip()
        if not instruction or instruction.lower() in {"sair", "exit", "quit"}:
            feedback_queue.put("Encerrando loop AVSA.")
            break

        profile = infer_task_profile(instruction)
        request = TaskRequest(instruction=instruction, **profile)
        decision = RoutingDecision(
            model="claude-sonnet-4.5",
            provider="cloud-paid",
            notes="Fallback automático por exceção.",
        )
        results: List[TaskResult] = []
        backlog.push()
        try:
            decision = smart_router.route(request)
            request.context["model"] = decision.model
            results = orchestrator.run(request)
        except Exception as exc:  # noqa: BLE001
            results = [TaskResult(status="failed", output=str(exc))]
        finally:
            backlog.complete()

        payload = {
            "timestamp": time.time(),
            "instruction": instruction,
            "routing": decision.__dict__,
            "results": [result.__dict__ for result in results],
        }
        persist_history(log_file, payload)

        summary_lines = [
            f"Modelo: {decision.model} ({decision.provider})",
            f"Rotas: {decision.notes}",
        ]
        summary_lines.extend(f"{idx+1}. {res.output}" for idx, res in enumerate(results))
        feedback_queue.put("\n".join(summary_lines))

    feedback_queue.put(None)
    announcer_thread.join(timeout=1)


if __name__ == "__main__":
    main()
