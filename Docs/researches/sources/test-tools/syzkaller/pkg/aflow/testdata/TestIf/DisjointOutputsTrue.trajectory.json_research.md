# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/DisjointOutputsTrue.trajectory.json

Purpose: golden trajectory for an `If` with disjoint outputs where the true branch runs.

Important structure: 6 spans total: flow, `If`, and `do` action start/finish pairs. Final result is `{"DoDone":"do","ElseDone":""}`.

Control flow: the true condition executes the `do` branch and skips `else`. The skipped branch's output remains a zero value while preserving the full output schema.

State and persistence: persistent golden data for branch output merge behavior.

Dependencies and integration: consumed by `If` tests and validates output extraction from branch-specific actions.

Risks and test signals: catches regressions in disjoint output verification, zero-value defaults, or branch span naming.
