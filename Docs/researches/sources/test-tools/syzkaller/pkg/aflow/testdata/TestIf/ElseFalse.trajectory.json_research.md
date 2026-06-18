# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/ElseFalse.trajectory.json

Purpose: golden trajectory for an `If` with an else branch where the condition is false.

Important structure: 6 spans total: flow, `If`, and `else-body` action start/finish pairs. Final result is `{"Done":"else"}`.

Control flow: false condition causes `else-body` to execute; `if-body` is not present in the span stream.

State and persistence: stores deterministic spans, condition args, and else result.

Dependencies and integration: consumed by `If` tests through the common runner.

Risks and test signals: detects regressions in false-branch dispatch, final result propagation, and wrapper span closure after else execution.
