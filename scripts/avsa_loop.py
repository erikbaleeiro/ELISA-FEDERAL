"""AVSA conversational loop com fallback textual.

Executa fluxo "feijão com arroz" entre instruções de voz/texto e agentes
CrewAI placeholders. Substitua os stubs pelas integrações reais.
"""
from __future__ import annotations

import json
import os
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional


@dataclass
class AgentSpec:
    name: str
    role: str
    handler: Callable[["TaskRequest"], "TaskResult"]


@dataclass
class TaskRequest:
    instruction: str
    context: Dict[str, str] = field(default_factory=dict)


@dataclass
class TaskResult:
    status: str
    output: str
    artifacts: Dict[str, str] = field(default_factory=dict)


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
    return TaskResult(status="ok", output=f"L2MAC gerou código para: {task.instruction}")


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


def main() -> None:
    voice = VoiceIO()
    orchestrator = CrewOrchestrator(build_default_agents())
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

        request = TaskRequest(instruction=instruction)
        results = orchestrator.run(request)

        payload = {
            "timestamp": time.time(),
            "instruction": instruction,
            "results": [result.__dict__ for result in results],
        }
        persist_history(log_file, payload)

        summary_lines = [f"{idx+1}. {res.output}" for idx, res in enumerate(results)]
        feedback_queue.put("\n".join(summary_lines))

    feedback_queue.put(None)
    announcer_thread.join(timeout=1)


if __name__ == "__main__":
    main()
