# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ChatbotAgent.java

## Purpose
Main Recon chatbot orchestrator. It turns a user question into one or more safe internal Recon API calls and asks the configured LLM to summarize the returned data.

## Important APIs, Types, And Functions
declares `ChatbotAgent`, `ToolCall`; key fields include `LIST_KEYS_ENDPOINT_SUFFIX`, `API_V1_ROOT`, `ALLOWED_ENDPOINT_PREFIXES`, `llmClient`, `toolExecutor`, `apiSchema`, `toolSelectionPreamble`, `summarizationPrompt`, `fallbackPromptTemplate`, `maxToolCalls`; important methods include `processQuery`, `getToolCall`, `executeMultipleToolCalls`, `summarizeResponse`, `handleFallback`, `buildToolSelectionPrompt`, `buildSummarizationPrompt`, `buildSummarizationUserPrompt`, `buildClarificationForToolCalls`, `validateToolCallForExecution`, `buildResponseKey`, `createExecutionMetadataMap`.

## Control Flow
`processQuery` validates the query, selects an LLM model, asks the LLM for a typed tool-call JSON envelope, handles documentation/fallback paths, enforces endpoint allowlist and safe listKeys scoping, executes calls through `ToolExecutor`, attaches pagination/limit metadata, and performs a second LLM summarization call.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with Ozone configuration, LLM client, Recon chatbot tool execution. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are prompt/schema drift, LLM malformed output, endpoint allowlist gaps, unbounded listKeys scans if safe scope is relaxed, summarization token growth, partial multi-call failures, and leaking internal error detail to users.

## Test Signals
Tests should mock `LLMClient` and `ToolExecutor` for single, multi, documentation, fallback, malformed JSON, disallowed endpoint, listKeys safe-scope, executor failure, and max-tool-call truncation paths.
