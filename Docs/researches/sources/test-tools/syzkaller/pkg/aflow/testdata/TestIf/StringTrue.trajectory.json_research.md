# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/StringTrue.trajectory.json

Purpose: golden trajectory for string condition truthiness where a non-empty string is true.

Important structure: 6 spans total: flow, `If`, and `if-body` start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: non-empty string condition executes the body and propagates `Done`.

State and persistence: persistent golden JSON for the runner harness.

Dependencies and integration: consumed by `If` tests for string condition support.

Risks and test signals: detects changes to string truthiness, branch execution, or span nesting.
