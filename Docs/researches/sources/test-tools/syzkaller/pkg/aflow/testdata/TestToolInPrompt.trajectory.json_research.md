<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.trajectory.json

## Purpose
This trajectory is the execution golden for `TestToolInPrompt`. It verifies that an agent with rendered tool references in prompt/instruction can complete with a plain text reply.

## Important APIs, Types, and Functions
It records `LLMAgent` and LLM spans, but no tool span, because the mocked model does not call `swiss-knife`. It still depends on `NewFuncTool` verification and template rendering during agent setup.

## Control Flow
The file has 6 spans: 2 flow, 2 agent, and 2 LLM spans. The agent sends its request, receives reply `Ignored`, records that reply, and the flow exports `Ignored`.

## State and Persistence
The trajectory persists final agent reply and flow result `{"Ignored":"Ignored"}`. It protects the behavior that declaring a tool and mentioning it in prompt text does not force its execution.

## Dependencies and Integration Points
It pairs with the LLM request fixture and integrates with final reply extraction. The absence of tool spans is meaningful and should remain stable unless the mocked replies change.

## Risks
If the framework starts enforcing tool use based on prompt text, this test would fail. If template rendering breaks earlier, the paired `.llm.json` catches it before trajectory comparison.

## Test Signals
Expected signals are no errors, no tool spans, final reply `Ignored`, and final flow result `Ignored`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.trajectory.json -->
