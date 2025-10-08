# Automated Voice Software Agent (AVSA)

The Automated Voice Software Agent (AVSA) is a collaborative team of AI-powered services designed to deliver fully automated software development from voice instructions. AVSA combines speech interfaces, intelligent orchestration, contextual knowledge management, automated coding, and continuous testing so that a single voice command can launch an entire development lifecycle.

## ✅ Resumo de decisão (Zero Cost First)

```yaml
cognição:
  primário: qwen-2.5-coder-32b-instruct   # local, $0
  fallback: claude-sonnet-4.5             # nuvem, só em edge cases

codificação:
  primário: qwen-2.5-coder-32b-instruct   # cobre 90% dos casos
  secundário: deepseek-coder-v2-lite-16b  # python rápido, 12 GB VRAM
  terciário: deepseek-r1                  # matemática pesada

multimodal:
  imagens: llava-v1.6-34b                # análise e OCR local
  áudio: whisper-large-v3                # transcrição local
  geração: sdxl-turbo + controlnet       # criação local

contexto:
  rag_local: haystack + bge-large-en-v1.5 + qdrant
  fallback_grátis: gemini-2.0-flash-exp  # até 1M tokens/dia

custo_mensal_estimado: "$5"
economia_vs_cloud: "92%"
```

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

## ⚡ ZeroCostRouter em ação

```python
from scripts.avsa_loop import TaskRequest, ZeroCostRouter, infer_task_profile

router = ZeroCostRouter()
profile = infer_task_profile("Planeja arquitetura crítica complexa")
model = router.route(TaskRequest(instruction="...", **profile))
print(model)  # claude-sonnet-4.5 apenas se for realmente crítico
```

O roteador avalia tipo de tarefa, complexidade, criticidade e uso diário antes de escalar para nuvem. A fila de feedback informa o modelo usado em cada iteração, garantindo rastreabilidade.

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

## Next Steps

- Integrate AVSA with ELISA-FEDERAL modules to enable voice-driven security scanning projects.
- Add analytics dashboards that visualize agent activity, code generation velocity, and test coverage.
- Extend the crew with deployment and monitoring agents for hands-off DevSecOps automation.

By relying on the Automated Voice Software Agent, teams can delegate repetitive engineering tasks to AI specialists and focus on strategic decisions that require human oversight.
