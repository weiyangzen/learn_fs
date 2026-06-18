<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.llm.json

## Purpose
This request fixture backs `TestTokenCompressionResetsHistory`. It verifies that after compression the agent can make another identical `tick` tool call without duplicate-call detection blocking it.

## Important APIs, Types, and Functions
It covers `LLMAgent.compressTokens`, `agentSession.toolHistory`, `recordAndCheckDuplicate`, compressor request construction, and `NewFuncTool` for `tick`.

## Control Flow
The array has 6 requests. Before compression, the history accumulates three identical `tick` calls. A compressor request summarizes that history. The resumed main request contains only prompt plus summary, and the final request records a fourth `tick` call/response after compression.

## State and Persistence
The fixture persists both request-history truncation and the reset duplicate-call context. The post-compression history lacks the prior three tool call records, which is the key state behavior under test.

## Dependencies and Integration Points
It integrates with token usage metadata in mocked responses, compressor prompting, and duplicate loop detection constants in `llm_agent.go`. The paired trajectory counts four successful `tick` executions.

## Risks
If compression leaves `toolHistory` intact, the fourth identical call would be rejected as a loop. If compression drops too much, the resumed request may lose the summary or prompt anchor.

## Test Signals
Expected signals are 6 requests, compressor invocation after three ticks, resumed two-message history, and a later accepted `id4` tick call.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.llm.json -->
