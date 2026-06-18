## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/LangChain4jDispatcher.java

Purpose: `LLMClient` implementation that routes chatbot requests through LangChain4j models while hiding provider-specific builders from higher layers.

Important APIs/types/functions: constructor registers providers with configured secrets; `chatCompletion` resolves provider/model, translates messages, executes a LangChain4j `ChatLanguageModel`, and returns `LLMResponse`; `getSupportedModels` returns configured models for available providers; `buildOpenAiModel`, `buildGeminiModel`, and `buildAnthropicModel` create provider clients; `resolveKey`, `resolveProvider`, `translateMessages`, and `parseModelList` handle routing details.

Control flow: provider is chosen from `_provider`, `provider:model`, or model-list reverse lookup. `buildModel` caches `(provider,model)` instances in a `ConcurrentHashMap`; failures evict the cache key. Gemini is intentionally routed through the OpenAI-compatible endpoint to honor timeouts.

State and persistence: no durable state; in-memory supported model map and model cache. Dependencies include LangChain4j OpenAI/Anthropic models, `CredentialHelper`, and chatbot configuration keys. It integrates with `/chatbot/models`, endpoint health, and agent calls.

Risks: provider hints are trusted before checking that the provider is configured, so an unknown/unconfigured provider errors later. Concurrent first-use can build duplicate model instances. `parameters` is used only for `_provider`, not general generation controls. Tests should cover provider resolution precedence, missing secrets, model-cache eviction on failure, message role fallback, token usage null handling, configured base URLs, and supported-model list behavior.
