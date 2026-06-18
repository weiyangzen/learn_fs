# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/ChatbotException.java

## Purpose
Typed checked exception used to wrap chatbot processing, LLM, and tool execution failures for the endpoint layer.

## Important APIs, Types, And Functions
declares `ChatbotException`.

## Control Flow
Provides message-only and message-plus-cause constructors; no additional state.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with plain Java/JDK DTO support. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are schema drift between DTO field names and UI/OpenAPI expectations, null/default handling, caller-supplied inconsistent counts, and weak coverage because many fields are pass-through values.

## Test Signals
Tests should verify endpoint exception translation preserves messages and causes.
