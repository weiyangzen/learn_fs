# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceNil.trajectory.json

Purpose: golden trajectory for slice condition truthiness where nil slice is false.

Important structure: 4 spans total: flow and `If` start/finish pairs. Final result is `{"Done":""}`.

Control flow: nil slice condition does not execute `if-body`.

State and persistence: persistent golden span fixture.

Dependencies and integration: consumed by `If` tests and complements `SliceEmpty` and `SliceTrue`.

Risks and test signals: detects regressions that distinguish nil and empty slices incorrectly for false-case branch selection.
