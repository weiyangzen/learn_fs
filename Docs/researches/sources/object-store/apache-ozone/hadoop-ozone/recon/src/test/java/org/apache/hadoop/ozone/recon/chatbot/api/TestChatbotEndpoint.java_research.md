# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/api/TestChatbotEndpoint.java

Purpose: This test suite validates the REST-level contract of `ChatbotEndpoint`, before and around agent execution. It covers input validation, successful and fallback responses, disabled feature behavior, generic error shielding, request timeout, executor queue saturation, singleton reuse, health reporting, model listing, and model-list failure handling.

Important APIs/types/functions: The class uses `ChatbotEndpoint.chat`, `health`, `getSupportedModels`, `shutdown`, `ChatbotEndpoint.ChatRequest`, `ChatbotEndpoint.ChatResponse`, `ChatbotAgent.processQuery`, `LLMClient.isAvailable`, `LLMClient.getSupportedModels`, `ChatbotException`, `Response`, and concurrency primitives `CountDownLatch`, `ExecutorService`, `Future`, `AtomicInteger`, and `AtomicReference`.

Control flow: `setUp` enables the chatbot, configures thread pool size, queue size, and request timeout, and constructs the endpoint with mocked agent/client. Validation tests call `chat` directly and inspect `Response`. Success tests stub the agent. Disabled tests create separate endpoint instances with feature toggle off. Timeout and queue tests construct short-timeout or small-queue endpoints and use blocking agent answers to force endpoint-level rejection or timeout paths.

State and persistence behavior: There is no persistence. Runtime state includes the endpoint's internal executor service, bounded queue, timeout configuration, enabled flag, and LLM client availability/model list. `tearDown` calls `shutdown` to release endpoint worker threads after each test.

Dependencies and integration points: This suite is the HTTP boundary for the chatbot feature. It integrates REST response mapping with agent exceptions, feature toggles, request admission control, asynchronous execution, health checks, and LLM model discovery. It confirms fallback text from the agent is a successful HTTP 200, not an error.

Risks: Concurrency tests use sleeps/latches and can be timing-sensitive, though timeouts are generous. Queue saturation asserts at least six 503 responses rather than an exact distribution because scheduling can vary. The endpoint is tested directly rather than through a Jersey container, so serialization annotations and network filters are outside scope.

Test signals: 400 with exact `Query cannot be empty`; 200 with `success=true` and response body for normal and fallback answers; 503 for disabled chat/models; 500 with generic error and no class/stack/rate-limit leak; 504 within two seconds for a 200 ms timeout; at least six queue-full 503s containing `too many requests`; five repeated calls routed to the same agent; health `enabled` and `llmClientAvailable` booleans; model list containing `gemini-2.5-flash`; and 500 for model provider exception.
