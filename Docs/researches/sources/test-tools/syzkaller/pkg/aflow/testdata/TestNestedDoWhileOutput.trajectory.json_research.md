<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileOutput.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileOutput.trajectory.json

## Purpose
This trajectory is the golden trace for `TestNestedDoWhileOutput` in `loop_test.go`. It verifies that a variable produced inside an inner `DoWhile` loop remains visible to a later action in the containing outer loop body.

## Important APIs, Types, and Functions
The fixture records `DoWhile.execute`, `DoWhile.loop`, `Pipeline`, and `NewFuncAction` behavior through `trajectory.Span`. It specifically covers loop variable discovery in `DoWhile.verify`, where loop-body outputs are collected and zero-initialized before execution.

## Control Flow
The file has 14 spans: 2 flow, 4 loop, 4 iteration, and 4 action spans. The outer loop runs one iteration. Inside it, the inner loop runs one iteration and `inner-action` returns `InnerContinue: ""` and `Leaked: "val"`. After the inner loop finishes, `outer-consumer` receives `Leaked` and returns `Continue: ""`, ending the outer loop.

## State and Persistence
The fixture persists the expected state handoff in span results: `Leaked` is produced by `inner-action` and then consumed by `outer-consumer`. It is a static golden file, but it protects runtime `ctx.state` behavior for nested loop variables.

## Dependencies and Integration Points
It integrates with the loop verification and execution machinery in `loop.go` and the test harness trajectory comparison. It also indirectly depends on reflect-based output type collection and map-backed workflow state.

## Risks
The main risk is incorrectly scoping loop variables so inner-loop outputs are cleared before outer actions can use them. Changes to loop variable initialization or nested loop verification could cause a missing input panic or a test failure in `outer-consumer`.

## Test Signals
The expected signal is a clean trajectory with no errors and final flow results `{}`. The visible result chain includes `Leaked: "val"` from `inner-action` and `Continue: ""` from `outer-consumer`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileOutput.trajectory.json -->
