# sources/test-tools/syzkaller/pkg/aflow/testdata/TestDoWhileMaxIters.trajectory.json

Purpose: golden trajectory for the do-while max-iteration failure path.

Important structure: 16 spans total: 2 flow, 2 loop, 6 iteration, and 6 action spans. Names include `test`, loop iterations `0`, `1`, `2`, and action `nop`.

Control flow: each iteration runs `nop`, which returns `Error: failed`. Because the `While` variable remains non-empty, the loop continues until `MaxIterations: 3` is exhausted. The loop and flow finish with `DoWhile reached max iteration limit 3`.

State and persistence: persistent test fixture with deterministic times and serialized error fields. No external state is referenced.

Dependencies and integration: consumed by `TestDoWhileMaxIters` in `loop_test.go`, through `runner_test.go` golden comparison.

Risks and test signals: high signal for preserving error propagation from `DoWhile.loop` through loop and flow spans. It also detects accidental off-by-one changes in iteration naming or iteration count.
