## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/LLMClient.java

Purpose: provider-agnostic contract used by chatbot code to call LLM backends without depending on OpenAI, Gemini, Anthropic, or LangChain4j specifics.

Important APIs/types/functions: `chatCompletion(List<ChatMessage>, String, Map<String,Object>)`; `isAvailable()`; `getSupportedModels()`; DTO `ChatMessage`; DTO `LLMResponse` with content, model, token counts, metadata, and `getTotalTokens()`; checked `LLMException` with optional status code.

Control flow: this is an interface; implementations must normalize request and response behavior. The contract states API keys are resolved server-side via `CredentialHelper` and never provided per request.

State and persistence: no state. Dependencies are minimal Java collections plus documentation reference to credential helper. It integrates upward with `ChatbotAgent` and `ChatbotEndpoint`; `LangChain4jDispatcher` is the implementation in this subset.

Risks: nested DTO classes are immutable only for final fields but do not defensively copy metadata; callers can mutate passed metadata maps. Tests should assert implementation conformance: empty-message rejection, token accounting, metadata provider fields, supported model listing, and consistent exception wrapping.
