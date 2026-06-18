# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ChatbotUtils.java

## Purpose
Utility class for chatbot endpoint normalization, path canonicalization, allowlist prefix matching, listKeys scope checks, robust JSON extraction from LLM prose, integer parsing, JSON parsing, classpath resource loading, and HTTP response stream reading.

## Important APIs, Types, And Functions
declares `ChatbotUtils`; key fields include `API_V1_ROOT`; important methods include `normalizeEndpoint`, `canonicalizeEndpointPath`, `matchesAllowedPrefix`, `isBucketScopedListKeysPrefix`, `extractFirstJsonObject`, `parsePositiveInt`, `extractStringField`, `estimateRecordCount`, `parseJsonSafely`, `loadResourceFromClasspath`, `readInputStream`, `readErrorStream`.

## Control Flow
Security helpers reject blank, scheme-bearing, and path-traversal endpoints outside `/api/v1`; JSON extraction uses brace counting with string/escape awareness rather than a regex.

## State And Persistence Behavior
State is request/runtime state, configuration, loaded prompt/schema resources, and network/LLM/tool-call results. Durable cluster state remains behind the Recon APIs the chatbot calls.

## Dependencies And Integration Points
Integrates with Recon chatbot tool execution, HTTP client I/O. In practice this file is consumed by Recon REST resources, namespace/container/datanode services, UI-facing JSON serialization, and tests that assert API shape.

## Risks And Edge Cases
Main risks are path canonicalization bypasses, prefix boundary mistakes, malformed LLM JSON, silently empty classpath resources, and stream reads that concatenate lines without delimiters.

## Test Signals
Tests should cover path traversal, query-string stripping, prefix boundaries, bucket-scoped start prefixes, nested JSON extraction, malformed JSON, classpath misses, and error stream reads.
