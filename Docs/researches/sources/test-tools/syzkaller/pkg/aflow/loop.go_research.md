# sources/test-tools/syzkaller/pkg/aflow/loop.go

Purpose: implements loop actions for aflow: `DoWhile` for repeat-until-empty string conditions, and `ForEach` for iterating over slice inputs while injecting an item variable into state.

Important APIs/types/functions: `DoWhile` exposes `Do Action`, `While string`, `MaxIterations int`, and internal `loopVars`. `ForEach` exposes `List`, `Item`, `Do`, and internal `loopVars`. Both implement `execute(ctx *Context) error` and `verify(ctx *verifyContext)`. Execution emits `trajectory.SpanLoop` and `trajectory.SpanLoopIteration` spans.

Control flow: `DoWhile.execute` opens a loop span, calls `loop`, then closes the span with any error. `loop` zero-initializes body-produced loop variables, runs body iterations up to `MaxIterations`, exits when `ctx.state[While].(string) == ""`, and errors on limit exhaustion. `ForEach.execute` validates the list exists and is a slice, opens a loop span named `ForEach`, zero-initializes body outputs, injects `Item` per element, executes the body, and deletes `Item` at the end.

State and persistence: state is entirely in-memory `ctx.state`. `DoWhile` permits loop variable redefinition to support nested loops and resets loop-carried values before entry. `ForEach` is stricter: loopVars must not already exist at runtime, and `Item` is temporary.

Dependencies and integration: uses `reflect` for type-aware zero values and slice inspection, `maps.Clone` for verification snapshots, and `trajectory` for event emission. It integrates with the broader `Action` verification model where outputs and inputs are checked in separate passes.

Risks and test signals: risks include panics if `While` is not string despite verification, leaked loop variables, duplicate names across loop boundaries, and failure to close spans correctly on body errors. `loop_test.go` covers normal do-while, max-iteration failure, nested-loop variable behavior, and `ForEach` typing/usage errors.
