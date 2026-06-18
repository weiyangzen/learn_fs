# sources/test-tools/syzkaller/pkg/aflow/testdata/TestForEach/Basic.trajectory.json

Purpose: golden trajectory for the basic `ForEach` list-processing test.

Important structure: 16 spans total: 2 flow, 2 loop, 6 iteration, and 6 action spans. Loop name is `ForEach`; iterations are `0`, `1`, and `2`; action is `process-item`.

Control flow: the flow enters a `ForEach` loop over `["a","b","c"]`. Each iteration injects the current `Item` and appends the uppercase value to `Result`, producing `["A","B","C"]`.

State and persistence: persistent golden JSON captures deterministic spans and per-action results. It does not persist temporary `Item`, which is deleted after loop execution.

Dependencies and integration: consumed by `TestForEach/Basic` in `loop_test.go`, and validates `ForEach.execute` span behavior and accumulator state.

Risks and test signals: catches regressions in item injection, accumulator zero-value initialization, iteration span names, temporary item cleanup side effects, and final output extraction.
