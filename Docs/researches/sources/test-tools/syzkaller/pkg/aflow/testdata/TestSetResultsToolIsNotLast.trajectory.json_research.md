<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSetResultsToolIsNotLast.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSetResultsToolIsNotLast.trajectory.json

## Purpose
This trajectory is the execution golden for `TestSetResultsToolIsNotLast`. It proves that a structured output captured by `set-results` survives a subsequent normal tool invocation and final text reply.

## Important APIs, Types, and Functions
It records spans for `LLMAgent`, the synthetic `set-results` tool, and a normal `tool` created by `NewFuncTool`. It validates session output retention and final state export.

## Control Flow
The file has 14 spans: 2 flow, 2 agent, 6 LLM, and 4 tool spans. The agent receives `set-results`, executes it, receives and executes `tool`, then receives final reply `Done`. The final flow result includes both `Reply: Done` and `Result: 42`.

## State and Persistence
The fixture persists intermediate `Result: 42`, empty normal tool result, final reply, and combined flow results. It protects `agentSession.outputs` from being overwritten or cleared by unrelated tool calls.

## Dependencies and Integration Points
It pairs with the request fixture and depends on deterministic trajectory nesting and ordering for mixed tool types. It also depends on `LLMAgent.Outputs` and `Reply` coexisting.

## Risks
A regression in output lifetime can drop `Result`. A regression in finalization can require set-results to be last, causing additional missing-output prompts and trajectory drift.

## Test Signals
Expected signals are no errors, tool spans for both `set-results` and `tool`, final reply `Done`, and final results `{"Reply":"Done","Result":42}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSetResultsToolIsNotLast.trajectory.json -->
