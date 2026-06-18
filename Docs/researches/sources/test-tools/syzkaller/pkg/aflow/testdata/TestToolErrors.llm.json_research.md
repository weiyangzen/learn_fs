<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.llm.json

## Purpose
This request fixture backs `TestToolErrors` in `func_tool_test.go`. It records how tool errors are returned to the model as function responses.

## Important APIs, Types, and Functions
It exercises `NewFuncTool`, `BadCallError`, normal Go errors from tool execution, genai function responses, and the `faulty` tool schema with boolean `CallError`.

## Control Flow
The array has 2 requests. The first declares tool `faulty`. The second request includes a `faulty` function call with `CallError: true` and a function response containing error text `you are wrong`. The next mocked reply in the Go test makes a hard-error call that is represented in the trajectory.

## State and Persistence
This file persists request history after a recoverable bad-call error. It does not include the later terminal hard error request because the test stops when the hard error fails the flow.

## Dependencies and Integration Points
It integrates with function response encoding, tool schema generation, and the agent loop that allows the model to correct bad calls. The trajectory captures the later hard error and final failure text.

## Risks
If all tool errors become fatal, this fixture would have no second request. If bad-call errors are not returned to the model, correction workflows break.

## Test Signals
Expected signals are the `faulty` declaration, one function call with `CallError: true`, and a function response error `you are wrong`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.llm.json -->
