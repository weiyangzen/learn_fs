# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentToolCallParsing.java

Purpose: This suite tests `ChatbotAgent.processQuery` orchestration after the first LLM call: JSON extraction, tool-call type routing, executor invocation, second LLM summarization, fallback routing, max-tool-call capping, malformed output handling, input validation, and exception wrapping.

Important APIs/types/functions: Key elements are `ChatbotAgent`, `LLMClient.LLMResponse`, `LLMClient.LLMException`, `ToolExecutor.ToolExecutionOutcome`, `ChatbotException`, `ChatbotConfigKeys`, and Mockito verification for `chatCompletion` and `executeToolCallWithPolicy`. Canned JSON constants cover `SINGLE_ENDPOINT`, `MULTI_ENDPOINT`, and `DOCUMENTATION_QUERY`.

Control flow: `setUp` enables the chatbot with safe-scope and max five tool calls. Happy-path tests return a tool JSON, verify one executor call for single endpoint or two for multi-endpoint, and require a second LLM call for summarization. Documentation queries return an answer directly with no executor and no second LLM call. Unknown or malformed outputs trigger fallback, which uses a second LLM call but no executor. Exception tests verify initial LLM, executor, and summarization failures are surfaced as `ChatbotException`.

State and persistence behavior: There is no persistence. Runtime state is primarily the parsed tool-call model, the bounded list of multi-endpoint calls, empty-map substitution for null/wrong `parameters`, and invocation counts. Empty and null user queries are rejected before any LLM state is touched.

Dependencies and integration points: This is the main behavioral contract for the chatbot agent's LLM-to-Recon pipeline. It integrates `ChatbotUtils` extraction behavior, JSON field parsing, endpoint/method/parameter routing, the executor policy method, fallback prompting, and summarization. It also validates that empty endpoints are never sent to lower layers.

Risks: The multi-endpoint cap uses `atMost(5)`, so it verifies a ceiling but not exact truncation behavior. The tests do not inspect constructed prompts or response bodies beyond non-null/string fragments. Unknown type and missing fields rely on fallback text from the mocked LLM rather than exact internal fallback prompt shape.

Test signals: One executor plus two LLM calls for single endpoint; two executor calls plus two LLM calls for two endpoint JSON; direct documentation response with one LLM call; fallback paths for unknown type, missing type, truncated JSON, prose, sentinel, empty tool-call arrays, and empty endpoint; early `ChatbotException` for empty/null query; empty-map resilience for bad `parameters`; max five tool calls; and cause preservation for LLM/executor failures.
