# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotModule.java

## Purpose
Guice module binding all chatbot components into Recon dependency injection.

## Important APIs, Types, And Functions
declares `ChatbotModule`; important methods include `configure`.

## Control Flow
`configure` binds `ChatbotEndpoint`, `ChatbotAgent`, `LLMClient`, `LangChain4jDispatcher`, `ToolExecutor`, and `CredentialHelper` as singletons.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with LLM client, Recon chatbot tool execution. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify injector creation and that chatbot components resolve only when the feature is enabled in higher-level wiring.
