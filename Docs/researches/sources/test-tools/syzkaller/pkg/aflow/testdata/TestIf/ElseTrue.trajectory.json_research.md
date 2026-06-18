# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/ElseTrue.trajectory.json

Purpose: golden trajectory for an `If` with an else branch where the condition is true.

Important structure: 6 spans total: flow, `If`, and `if-body` action start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: true condition executes `if-body` and skips `else-body`.

State and persistence: persistent fixture containing deterministic span timings and branch result.

Dependencies and integration: consumed by `If` tests and validates branch choice with an available else branch.

Risks and test signals: catches regressions where both branches execute, the wrong branch runs, or branch results fail to propagate.
