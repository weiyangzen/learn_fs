<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.trajectory.json

## Purpose
This trajectory is the execution golden for `TestToolErrors`. It distinguishes recoverable bad-call feedback from terminal hard tool failure.

## Important APIs, Types, and Functions
It records `LLMAgent`, LLM spans, and tool spans for `faulty`. It covers `BadCallError`, ordinary `error`, tool execution result/error recording, and final flow error propagation.

## Control Flow
The file has 12 spans: 2 flow, 2 agent, 4 LLM, and 4 tool spans. The first tool call errors with `you are wrong`, which is returned to the model. The second call uses `CallError: false`, the tool returns `hard error`, and the agent/flow finish with `tool faulty failed: error: hard error args: map[CallError:false]`.

## State and Persistence
The fixture persists both tool error spans and the propagated terminal error. It protects the state transition from recoverable model feedback to fatal workflow error.

## Dependencies and Integration Points
It pairs with the LLM request fixture and depends on error string formatting in tool wrappers. It also integrates with trajectory error fields on tool, agent, and flow spans.

## Risks
Changing error formatting can break golden comparisons. More importantly, conflating `BadCallError` with hard errors would either stop too early or continue after a real failure.

## Test Signals
Expected signals are tool error `you are wrong`, later `hard error`, and final flow error text naming tool `faulty` and its args.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.trajectory.json -->
