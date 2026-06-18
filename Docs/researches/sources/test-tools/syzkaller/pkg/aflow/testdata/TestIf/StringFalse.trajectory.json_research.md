# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/StringFalse.trajectory.json

Purpose: golden trajectory for string condition truthiness where an empty string is false.

Important structure: 4 spans total: flow and `If` start/finish pairs. Final result is `{"Done":""}`.

Control flow: empty string condition skips the body.

State and persistence: persistent golden fixture with deterministic timestamps.

Dependencies and integration: consumed by `If` tests and parallels integer/slice false cases.

Risks and test signals: catches regressions in string truthiness and zero-value final output behavior.
