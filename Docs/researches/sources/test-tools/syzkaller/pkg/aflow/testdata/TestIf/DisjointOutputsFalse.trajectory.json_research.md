# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/DisjointOutputsFalse.trajectory.json

Purpose: golden trajectory for an `If` with disjoint outputs where the false branch runs.

Important structure: 6 spans total: flow, `If`, and `else` action start/finish pairs. Final result is `{"DoDone":"","ElseDone":"else"}`.

Control flow: the condition evaluates false, so the `else` branch executes and the `do` branch is skipped. The missing branch output is represented as its zero value.

State and persistence: persistent golden fixture records branch choice and final merged output shape.

Dependencies and integration: consumed by `If` tests that verify branch output reconciliation.

Risks and test signals: detects regressions in branch-disjoint output handling, zero-value filling for skipped branch outputs, and else branch span naming.
