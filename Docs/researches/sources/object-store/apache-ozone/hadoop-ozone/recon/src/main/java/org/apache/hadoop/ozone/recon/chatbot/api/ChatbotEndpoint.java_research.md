## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/api/ChatbotEndpoint.java

Purpose: JAX-RS singleton REST resource for `/chatbot`, exposing health, chat, and model-list APIs for the Recon chatbot.

Important APIs/types/functions: `health()` returns enabled and LLM availability flags; `chat(ChatRequest)` validates input, submits query processing to a bounded executor, and converts failures into HTTP responses; `getSupportedModels()` delegates to `LLMClient`; `shutdown()` tears down the executor; DTOs `ChatRequest` and `ChatResponse` are Jackson-friendly and ignore unknown fields.

Control flow: constructor reads pool and queue sizes from `ChatbotConfigKeys` and builds a fixed `ThreadPoolExecutor` backed by `ArrayBlockingQueue`. `chat` rejects disabled service and blank query, logs sanitized user/model/provider, submits `chatbotAgent.processQuery(query, model, provider)`, waits with configured request timeout, returns 200 on success, 503 on saturation/interruption, 504 on timeout, and 500 on execution failure.

State and persistence: no DB state; it owns an in-process executor. Dependencies are Guice/JAX-RS, `ChatbotAgent`, `LLMClient`, `OzoneConfiguration`, and chatbot config keys. Integration with Recon module wiring depends on the same enabled check used by controller installation.

Risks: `request` is dereferenced before null checking, so a null JSON body can throw. Blocking `Future#get` still occupies the request thread, though bounded by pool/queue. `Future.cancel(true)` relies on downstream interruption support. Tests should cover disabled mode, blank/null query, executor saturation, timeout, model errors, sanitized logging behavior, and lifecycle shutdown.
