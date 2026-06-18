# sources/test-tools/syzkaller/prog/collide.go

Purpose: implements program transformations intended to trigger race conditions by assigning async/rerun properties and duplicating calls.

Important APIs/types/functions: `maxAsyncPerProg`, `AssignRandomAsync`, `AssignRandomRerun`, `DoubleExecCollide`, and `DupCallCollide`.

Control flow and state: `AssignRandomAsync` clones the program and walks calls backward, avoiding async producers whose resources are needed too soon, never marking the last call async, and capping async calls at 24. `AssignRandomRerun` assigns rerun counts to selected adjacent async pairs. `DoubleExecCollide` appends a clone of all calls and marks the duplicate prefix async. `DupCallCollide` randomly selects up to one third of calls, inserts async duplicates before originals, and respects `MaxCalls`.

Dependencies and integration: depends on `Clone`, `cloneCalls`, `cloneCall`, `ForeachArg`, resource direction semantics, `CallProps`, and executor thread limits described in comments.

Risks: async assignment is a heuristic and cannot guarantee producer completion. Duplicating with `cloneCalls(..., nil)` intentionally leaves duplicate resource references tied to first-half producers for double execution; changing this would alter collide semantics. Transformations must not exceed `MaxCalls` or executor async capacity.

Test signals: `collide_test.go` verifies resource-safe async placement, exact duplicate serialization with properties stripped, async insertion variants, and expected failure for too-small/too-large inputs.
