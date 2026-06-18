# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/llm/TestLangChain4jDispatcher.java

Purpose: This suite tests `LangChain4jDispatcher` provider availability, supported-model discovery, validation, and provider routing without making real network calls. It verifies configured API keys control availability/model lists, unknown or unconfigured models are rejected, and explicit provider hints bypass model-list reverse lookup.

Important APIs/types/functions: The class uses `LangChain4jDispatcher.chatCompletion`, `isAvailable`, `getSupportedModels`, `LLMClient.ChatMessage`, `LLMClient.LLMException`, `CredentialHelper`, `OzoneConfiguration`, and chatbot provider/key config entries for Gemini, OpenAI, and Anthropic.

Control flow: Setup defaults provider to `gemini` and creates a dispatcher with no keys. Validation tests call `chatCompletion` with null/empty messages and expect `LLMException`. Availability/model tests mutate config keys and recreate the dispatcher. Routing tests either inspect `getSupportedModels` or call `chatCompletion` with missing keys and assert the resulting exception identifies the provider path or model recognition failure.

State and persistence behavior: No persistence is used. Runtime state is derived from configuration and `CredentialHelper` lookups. The dispatcher's supported model list changes based on which provider secrets are present.

Dependencies and integration points: This file anchors the chatbot LLM abstraction to provider-specific key configuration and model naming. It protects the `/api/v1/chatbot/models` endpoint contract indirectly by checking exposed model names and validates that a configured Gemini key does not accidentally route OpenAI model names to Gemini.

Risks: Tests avoid real LangChain4j clients and network calls, so request serialization, provider responses, token accounting, and actual model invocation are not covered. Model name assertions such as `gemini-2.5-flash`, `gpt-4.1`, and `claude-sonnet-4-6` are intentionally brittle compatibility signals and must be updated when supported lists change.

Test signals: `LLMException` for null/empty messages; `isAvailable=false` without keys and true with Gemini/OpenAI key; empty supported list without keys; provider-specific model names present with corresponding keys; unknown model errors mentioning `not recognised` and `GET /api/v1/chatbot/models`; OpenAI model rejected when only Gemini key exists; explicit `_provider=openai` and `anthropic:model` strings produce provider-specific missing-key errors rather than model-recognition errors.
