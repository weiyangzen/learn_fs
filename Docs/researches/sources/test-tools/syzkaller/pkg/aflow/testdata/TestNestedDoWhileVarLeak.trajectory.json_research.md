<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileVarLeak.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileVarLeak.trajectory.json

## Purpose
This trajectory is the golden trace for `TestNestedDoWhileVarLeak` in `loop_test.go`. It verifies that variables created inside a nested loop do not cause a duplicate-definition panic when the outer loop re-enters for another iteration.

## Important APIs, Types, and Functions
It covers `DoWhile.verify`, `DoWhile.loop`, `Pipeline`, and `NewFuncAction`. The key implementation point is `DoWhile.loop` resetting known loop variables to zero values at the start of loop execution while allowing redefinition for nested loops.

## Control Flow
The file has 28 spans: 2 flow, 6 loop, 8 iteration, and 12 action spans. The outer loop runs two iterations. Each outer iteration calls `outer-action`, then an inner one-iteration loop with `inner-action` producing `Leaked: "val"` and `consumer-action` consuming it. The first outer iteration returns `Continue: "yes"` and the second returns `Continue: ""`.

## State and Persistence
The persisted span results show `Continue`, `InnerContinue`, and `Leaked` across both outer iterations. The fixture protects the map-backed workflow state from retaining nested loop output metadata in a way that would conflict on the second pass.

## Dependencies and Integration Points
It integrates with reflect-based loop variable typing, nested `Pipeline` execution, and trajectory span nesting. The test harness expects all action, loop, and iteration spans in deterministic order.

## Risks
If nested loop outputs are treated as globally new outputs on every outer iteration, execution can fail on re-entry. If they are over-cleared, `consumer-action` may not see `Leaked`. Either behavior would show up as missing spans or non-empty span errors.

## Test Signals
The expected signal is a no-error trace with two outer iteration names, repeated `inner-action`/`consumer-action` spans, and final flow results `{}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileVarLeak.trajectory.json -->
