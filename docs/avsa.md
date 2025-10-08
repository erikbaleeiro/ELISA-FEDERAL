# Automated Voice Software Agent (AVSA)

The Automated Voice Software Agent (AVSA) is a collaborative team of AI-powered services designed to deliver fully automated software development from voice instructions. AVSA combines speech interfaces, intelligent orchestration, contextual knowledge management, automated coding, and continuous testing so that a single voice command can launch an entire development lifecycle.

## ✅ Resumo de decisão (Zero Cost First)

```yaml
camada_cognição:
  primário: qwen-2.5-coder-32b-instruct   # roda na GPU alugada
  fallback: claude-sonnet-4.5             # só quando a tarefa explode

camada_código:
  pesado: qwen-2.5-coder-32b-instruct     # arquitetura, refatoração séria
  médio: deepseek-coder-v2-lite-16b       # python/js diário
  matemático: deepseek-r1                 # otimização hardcore

camada_multimodal:
  imagem: llava-v1.6-34b
  áudio: whisper-large-v3
  geração: sdxl-turbo + controlnet

camada_contexto:
  rag_local: haystack + bge-large-en-v1.5 + qdrant
  fallback_grátis: gemini-2.0-flash-exp

deploy:
  frontend: vercel (builder.io + locofy + next.js)
  backend: render.com (fastapi + smart_router)
  gpu_pool: runpod/vast.ai (qwen-32b, llava, whisper)

custo_médio_mensal: "$19-23"  # perfil hobby
economia_vs_cloud: "92%"
```

## 🏗️ Arquitetura "Erik Stack"

```
┌─────────────────────────────────────────────────┐
│  FRONTEND (Visual)                              │
│  Builder.io → Locofy.ai → React/Next.js        │
│  Deploy: Vercel (free/pro tiers)               │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│  BACKEND (Orquestração)                        │
│  FastAPI + SmartRouter + Haystack              │
│  Deploy: Render.com (free/starter tiers)       │
└─────────────────────────────────────────────────┘
                        ↓
            ┌───────────┴───────────┐
            ↓                       ↓
┌─────────────────────┐   ┌─────────────────────┐
│  APIs em Nuvem      │   │  GPU Alugada        │
│  Claude 4.5         │   │  RunPod / Vast.ai   │
│  GPT-4o             │   │  Qwen-32B, LLaVA    │
│  Gemini Flash       │   │  Whisper, SDXL      │
└─────────────────────┘   └─────────────────────┘
```

Tudo gira em torno do **SmartRouter**: ele roda no backend FastAPI, mede backlog, complexidade e custo, liga/desliga a GPU alugada e decide se a tarefa fica no Qwen local, no Gemini gratuito ou escala para Claude/GPT-4o.

## System Overview

AVSA relies on a set of specialized agents coordinated by CrewAI:

- **Voice Interface (Gemini Live + Speech APIs):** Converts spoken requests into text and returns spoken feedback to the user in real time.
- **CrewAI Orchestrator:** Acts as the project manager, receiving transcribed instructions, delegating tasks, and ensuring overall progress.
- **Planning Agent:** Expands the request into a detailed execution plan and clarifies requirements when needed.
- **Search Agent (Haystack):** Retrieves contextual knowledge, documentation, and examples so downstream agents operate with up-to-date references.
- **Coding Agent (L2MAC):** Generates and updates application code following the plan and insights produced by other agents.
- **Testing Agent:** Writes and runs automated tests to verify functionality and surface defects.
- **Refactoring Agent:** Iteratively improves the implementation based on test results, feedback, or new requirements.

All agents share the same conversation context, eliminating repetitive restatement of goals and allowing the team to build on previous steps.

## End-to-End Workflow

1. **Voice Command:** The user issues a natural-language instruction such as “Create a Snake game.”
2. **Speech Processing:** Gemini Live streams the audio, converts it to text, and forwards it to CrewAI.
3. **Task Orchestration:** CrewAI’s project manager agent assigns subtasks (planning, research, coding, testing, refactoring) and sets success criteria.
4. **Planning & Research:** The Planning Agent produces an actionable roadmap while the Search Agent leverages Haystack to pull relevant documentation (for example, Flask API guides or game development best practices).
5. **Implementation:** L2MAC generates the required code artifacts, leveraging contextual notes and prior project history.
6. **Testing:** The Testing Agent designs and executes unit or integration tests, reporting outcomes back to CrewAI.
7. **Refinement:** The Refactoring Agent modifies the code base to resolve failing tests or incorporate follow-up feedback.
8. **Voice Feedback:** CrewAI summarizes progress and communicates status updates or clarification questions back through the voice interface.

This loop repeats automatically until the user confirms completion or provides new instructions.

## Automation Benefits

- **Lifecycle Coverage:** AVSA eliminates manual handoffs by chaining planning, coding, testing, and refactoring into a continuous pipeline.
- **Context Preservation:** Haystack keeps the full project history at every step, avoiding lost requirements and enabling consistent decision-making.
- **Natural Collaboration:** Voice-first interaction allows stakeholders to contribute without writing prompts or technical specifications.
- **Rapid Iteration:** Immediate feedback and code regeneration shorten debugging cycles and accelerate delivery.

## 🚦 SmartRouter & GPU sob demanda

- **Tarefas simples (complexidade ≤ 4):** Gemini Flash grátis direto, zero custo.
- **Código médio (≤ 7):** Qwen-32B/DeepSeek na GPU alugada. Se a GPU estiver desligada e o backlog ≥ 5 tarefas ou a estimativa ≥ 10 min, o SmartRouter liga a instância RunPod/Vast.ai automaticamente.
- **Multimodal:** LLaVA/Whisper locais quando a GPU está on-line; fallback GPT-4o só se estiver tudo desligado.
- **Crítico/complexo:** Claude Sonnet 4.5 sem rodeios.
- **Logs estruturados:** cada decisão gera provider + notas no `logs/avsa_history.log`.

O código referencial está em `scripts/avsa_loop.py` com as classes `TaskBacklog`, `GPUConnector` e `SmartRouter` integradas.

## 🧠 Estratégia Ultra-Realista

- **Local primeiro sempre:** GPUs consumidoras (RTX 3090/4090) rodam Qwen-32B em 4-bit com ~20 GB de VRAM.
- **Cache agressivo + batch:** reutiliza respostas em 7/30/90 dias e processa lotes para economizar tokens.
- **Prompt compression:** `llmlingua` reduz prompts em ~50% sem perder contexto crítico.
- **RAG local:** Haystack + BGE embeddings + Qdrant oferecem contexto virtualmente infinito sem custo recorrente.
- **Fallback consciente:** só recorrer a Claude 4.5 ou Gemini Flash quando o roteador sinalizar que o local não atende.

## Implementation Blueprint

1. **Configure APIs:** Provision Google Cloud Speech services and Gemini Live credentials for real-time transcription and synthesis.
2. **Install Dependencies:** `pip install crewai haystack l2mac SpeechRecognition pyttsx3` plus any platform-specific drivers (e.g., `pyaudio`).
3. **Build the Voice Interface:** Combine SpeechRecognition for microphone input with Gemini Live for transcription and pyttsx3 (or Google Cloud TTS) for spoken responses.
4. **Define CrewAI Agents:** Describe each agent’s role, goals, and accessible tools, then assemble them into a collaborative crew with the project manager orchestrator.
5. **Expose Tools:** Wrap Haystack search pipelines e o `ZeroCostRouter` para CrewAI ativar Qwen/DeepSeek localmente, usando Gemini Flash só como tier gratuito.
6. **Conversation Loop:** Use `scripts/avsa_loop.py` para rodar o fluxo com seleção automática de modelo e logging persistente.
7. **Continuous Improvement:** Adicione agentes de deploy/monitoramento mantendo o princípio "custo zero primeiro".

## 🚢 Deploy Híbrido (Render + GPU alugada)

1. **Frontend:** gerar UI no Builder.io → exportar com Locofy.ai → rodar Next.js. O arquivo `config/deploy/vercel.json` já deixa o deploy plug-and-play na Vercel.
2. **Backend FastAPI:** implemente o roteador na FastAPI, empacote no repositório e use `config/deploy/render.yaml` para subir no Render.com (starter tier fica em ~US$7/mês).
3. **GPU sob demanda:** alugue RunPod/Vast.ai quando necessário, aponte `GPU_SSH_HOST/PORT/USER` no Render e deixe o `GPUConnector` ligar/desligar o worker (veja a classe no script de loop).
4. **APIs externas:** mantenha as chaves em variáveis de ambiente seguras no Render (Anthropic/OpenAI/Gemini).

## ⚡ ZeroCostRouter em ação

```python
from scripts.avsa_loop import SmartRouter, TaskBacklog, TaskRequest, infer_task_profile

router = SmartRouter(backlog=TaskBacklog())
profile = infer_task_profile("Planeja arquitetura crítica complexa")
decision = router.route(TaskRequest(instruction="...", **profile))
print(decision)
```

O SmartRouter calcula backlog, tempo estimado e custo antes de escalar para nuvem. O `decision` retorna modelo, provedor e notas — os mesmos campos gravados no `logs/avsa_history.log`.

## Referência de implementação rápida

O script `scripts/avsa_loop.py` entrega um laço de conversação mínimo com ganchos para Gemini Live, Haystack e L2MAC. Ele usa entrada de texto como fallback quando as credenciais de voz não estão configuradas, garantindo validação rápida do fluxo sem dependências pesadas.

## Example Voice Session

```
"Start a new project called 'Client Management' and create a Code Creation Agent."
"Create an API in Python to register new clients. The Search Agent should consult the Flask API documentation to ensure correct implementation."
"Run the API and let me know if there are any errors."
"Create unit tests for the client registration route."
"Add validation to check if the email provided is valid."
"Delete the client listing functionality."
```

Each command flows through the pipeline above, triggering coordinated planning, research, coding, testing, and refactoring steps until the software meets the evolving specification.

## 💰 Perfis de custo realistas

| Perfil | Frontend | Backend | APIs | GPU | Total mensal |
|--------|----------|---------|------|-----|---------------|
| Hobby (10-20h) | Vercel $0 | Render $0 | $15 | $4-8 | **$19-23** |
| Freelancer (60-80h) | Vercel $20 | Render $7 | $60 | $24-32 | **$111-119** |
| Agência (24/7) | Vercel $20 | Render $25 | $120 | $250 | **$415** |

Os números estão refletidos em `config/zero_cost_stack.yaml`, que também lista economia anual e thresholds de auto-start da GPU.

## Next Steps

- Integrate AVSA with ELISA-FEDERAL modules to enable voice-driven security scanning projects.
- Add analytics dashboards that visualize agent activity, code generation velocity, and test coverage.
- Extend the crew with deployment and monitoring agents for hands-off DevSecOps automation.

By relying on the Automated Voice Software Agent, teams can delegate repetitive engineering tasks to AI specialists and focus on strategic decisions that require human oversight.
