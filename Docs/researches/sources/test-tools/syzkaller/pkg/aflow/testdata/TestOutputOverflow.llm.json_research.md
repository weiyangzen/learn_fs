<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.llm.json

## Purpose
This request fixture backs `TestOutputOverflow`. It captures how the agent lowers Gemini thinking levels after `FinishReasonMaxTokens` responses and resets thinking when the conversation advances.

## Important APIs, Types, and Functions
It exercises `LLMAgent.execute`, output overflow handling, genai `thinkingConfig`, `LLMOutputs`, and the synthetic `set-results` tool. The expected thinking sequence is `HIGH, MEDIUM, LOW, MINIMAL, HIGH, MEDIUM, LOW, MINIMAL`.

## Control Flow
The array has 8 requests. The first four are repeated initial prompt attempts with progressively reduced thinking. After a successful `set-results` call with `Output: 42`, the next four requests include that tool call/response in history and again step through the thinking levels until minimal thinking also overflows.

## State and Persistence
This fixture persists model config state across retries: system instruction, set-results schema, request history length, and thinking level. It does not store final workflow state, but it records when retry attempts reuse or extend conversation history.

## Dependencies and Integration Points
It integrates with genai finish reasons, aflow retry policy, and request construction. The trajectory file records the visible span-level errors `MAX_TOKENS`.

## Risks
Overflow recovery is sensitive to retry count and history management. A change that fails to lower thinking could keep overflowing; a change that fails to reset after a successful response would send later requests with too little reasoning budget.

## Test Signals
Expected signals are exactly 8 requests, the thinking level descent repeated twice, and preserved set-results history in the second half.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.llm.json -->
