<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.llm.json

## Purpose
This request fixture backs `TestTokenCompression`. It captures token-threshold based context compression, where the agent calls a cheaper compressor prompt and resumes with only the anchor prompt plus summary.

## Important APIs, Types, and Functions
It exercises private `LLMAgent.compressTokens`, `compressContext`, compressor instruction construction, `GoodBalancedModel` style compressor behavior, and normal `tick` tool declaration. It also records usage-triggered transition from full history to compressed history.

## Control Flow
The array has 4 requests. The agent first calls `tick`, then calls `tick` again after prompt token count grows. The third request is a compressor-model request containing system instructions wrapped in `<system_instructions>` and the prior tool history. The fourth request resumes the main model with two messages: original prompt and `Here is the summary... compressed summary`.

## State and Persistence
The file persists exact compression request content, temperature `0.1` for the compressor, and the truncated post-compression request. It protects the anchor-plus-summary invariant asserted by the Go test.

## Dependencies and Integration Points
It integrates with genai usage metadata from mocked responses, request history construction, and the trajectory that records a `smarty-compressor` LLM span. It also interacts with duplicate-tool-call detection because compression resets history in related tests.

## Risks
Compression can accidentally duplicate system instructions, lose the original prompt, retain too much old history, or summarize with tools enabled. This fixture checks that the compressor has no tools and that resumed main history is compact.

## Test Signals
Expected signals are 4 requests, a compressor request with the memory-compressor instruction, and a final main request containing only the prompt plus formatted summary.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.llm.json -->
