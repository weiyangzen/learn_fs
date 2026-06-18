# sources/test-tools/syzkaller/prog/collide_test.go

Purpose: verifies collide/race-oriented program transformations.

Important APIs/types/functions: `TestAssignRandomAsync`, `TestDoubleExecCollide`, and `TestDupCallCollide`.

Control flow and state: tests deserialize small Linux programs, repeatedly apply random transformations, and assert structural invariants. `TestAssignRandomAsync` ensures resource-producing calls are not made async when immediate consumers would break. `TestDoubleExecCollide` strips call props to compare duplicated call order. `TestDupCallCollide` samples up to 100 iterations and requires expected serialized variants to appear.

Dependencies and integration: uses `GetTarget`, `Deserialize`, `Serialize`, `Clone`, `CallProps`, random sources from `initTest`, and `testify/assert`.

Risks: random variant detection can be sensitive to iteration count and RNG changes. Exact serialization comparisons can fail on harmless formatter changes.

Test signals: covers async safety, clone/reference behavior for duplicated calls, `CallProps.Async` placement, and transformation error paths.
