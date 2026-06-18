# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/IntFalse.trajectory.json

Purpose: golden trajectory for integer condition truthiness where zero is false.

Important structure: 4 spans total: flow and `If` start/finish pairs. Final result is `{"Done":""}`.

Control flow: the `If` action logs a zero integer condition, skips `if-body`, and finishes.

State and persistence: persistent fixture with deterministic times and args/results.

Dependencies and integration: consumed by `If` tests that exercise non-boolean condition coercion.

Risks and test signals: catches regressions in integer truthiness, zero-value output handling, and condition argument serialization.
