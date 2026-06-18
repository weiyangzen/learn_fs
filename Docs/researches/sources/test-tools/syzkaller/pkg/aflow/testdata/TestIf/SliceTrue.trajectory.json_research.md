# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceTrue.trajectory.json

Purpose: golden trajectory for slice condition truthiness where a non-empty slice is true.

Important structure: 6 spans total: flow, `If`, and `if-body` start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: non-empty slice condition executes `if-body`.

State and persistence: persistent JSON fixture with deterministic span timing and result data.

Dependencies and integration: consumed by `If` tests for non-boolean condition support.

Risks and test signals: catches truthiness regressions for slices and body-output propagation changes.
