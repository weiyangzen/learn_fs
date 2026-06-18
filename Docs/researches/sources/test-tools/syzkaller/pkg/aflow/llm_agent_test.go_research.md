# sources/test-tools/syzkaller/pkg/aflow/llm_agent_test.go

## Purpose

`llm_agent_test.go` verifies LLM runtime error classification, retry backoff, summary window behavior, token compression, structured outputs, output overflow handling, validated outputs/replies, nil tool args, tool template variables, and registration errors.

## Important APIs, Types, and Functions

Tests call `parseLLMError`, `llmBackoffDuration`, `testFlow`, `LLMAgent`, `LLMOutputs`, `ValidatedLLMOutputs`, `LLMReply`, and helper `createToolCallResponse`. They construct `genai.APIError`, `GenerateContentResponse`, `FunctionCall`, and `Part` stubs.

## Control Flow

Error tests map specific HTTP/provider messages to retry, quota, input overflow, output overflow, or raw errors and verify max retry behavior. Compression tests simulate token counts that exceed thresholds and assert history truncates to anchor plus summary and duplicate-call history resets. Structured-output tests verify `set-results` can be non-last, output-only agents can finish after set-results, validators can reject or rewrite results, and output-token overflow progressively lowers thinking level before failing. Registration tests assert invalid template functions, tool names, duplicate tools, mutually exclusive context options, and reply conflicts are caught.

## State and Persistence Behavior

All model calls are stubbed in-memory through the test harness. Token compression changes per-session request history only. No real model or persistent cache behavior is exercised beyond the harness.

## Dependencies and Integration Points

It depends on GenAI response shapes, aflow test helpers, and `testify`. It is the primary safety net for the complex LLM/tool protocol.

## Risks and Edge Cases

Provider error parsing tests encode exact message substrings; provider changes may require updates. Tests verify compression mechanics but not semantic quality of summaries. They do not cover real network behavior.

## Test Signals

The suite is high-value for preventing regressions in retry behavior, context management, structured output contracts, and validator feedback loops.
