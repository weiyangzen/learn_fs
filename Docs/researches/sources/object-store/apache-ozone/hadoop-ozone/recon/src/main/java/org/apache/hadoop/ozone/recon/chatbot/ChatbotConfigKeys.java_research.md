# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotConfigKeys.java

## Purpose
Central configuration key registry for the Recon chatbot feature, including enablement, provider/model defaults, API keys/base URLs, execution limits, thread pool/queue sizes, provider model lists, and Anthropic beta header.

## Important APIs, Types, And Functions
declares `ChatbotConfigKeys`; key fields include `OZONE_RECON_CHATBOT_PREFIX`, `OZONE_RECON_CHATBOT_ENABLED`, `OZONE_RECON_CHATBOT_ENABLED_DEFAULT`, `OZONE_RECON_CHATBOT_PROVIDER`, `OZONE_RECON_CHATBOT_PROVIDER_DEFAULT`, `OZONE_RECON_CHATBOT_DEFAULT_MODEL`, `OZONE_RECON_CHATBOT_DEFAULT_MODEL_DEFAULT`, `OZONE_RECON_CHATBOT_TIMEOUT_MS`, `OZONE_RECON_CHATBOT_TIMEOUT_MS_DEFAULT`, `OZONE_RECON_CHATBOT_OPENAI_API_KEY`; important methods include `isChatbotEnabled`.

## Control Flow
`isChatbotEnabled` reads `ozone.recon.chatbot.enabled` from `OzoneConfiguration`; all other members are constants consumed by the chatbot module, endpoint, LLM client, agent, executor, and credential helper.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with Ozone configuration, Recon chatbot tool execution. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should cover default disabled behavior, explicit enablement, config key spelling, and default limits used by dependent classes.
