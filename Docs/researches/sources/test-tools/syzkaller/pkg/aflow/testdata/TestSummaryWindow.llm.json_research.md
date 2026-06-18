<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.llm.json

## Purpose
This request fixture backs `TestSummaryWindow`. It captures sliding-window summarization behavior when an agent keeps only a limited number of historical messages and asks the model to attach summaries before old context is dropped.

## Important APIs, Types, and Functions
It exercises private `LLMAgent.summaryWindow`, `slidingWindowInstruction`, request trimming, function tool history, and `NewFuncTool` declaration for `tick`. The tool has `Seq` input and `ResFoo` output.

## Control Flow
The array has 8 requests. The first declares `tick`; later requests alternate `tick` calls and responses. When the window threshold is reached, the request includes `slidingWindowInstruction` appended to a user message. Subsequent requests preserve a model summary text such as `summary 3` while older calls are trimmed.

## State and Persistence
The fixture persists exact conversation slices after windowing: request lengths alternate between compact 3-message windows and 4-message summary-producing windows. It protects `summaryMessage` tracking inside `agentSession`.

## Dependencies and Integration Points
It integrates with genai content roles, tool call/function response serialization, and trajectory recording. The paired trajectory confirms repeated tool execution and final reply.

## Risks
Sliding-window logic can drop useful tool output too early, duplicate summaries, or fail to request a summary before trimming. Those changes would appear as request history length or instruction placement differences.

## Test Signals
Expected signals are 8 requests, repeated `tick` calls, inserted `slidingWindowInstruction`, summaries in model messages, and final completion after request sequence exceeds 6.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.llm.json -->
