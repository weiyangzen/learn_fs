# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceEmpty.trajectory.json

Purpose: golden trajectory for slice condition truthiness where an empty non-nil slice is false.

Important structure: 4 spans total: flow and `If` start/finish pairs. Final result is `{"Done":""}`.

Control flow: the `If` action records the condition and skips the body because the slice is empty.

State and persistence: persistent deterministic trajectory, with no durable state beyond JSON fixture data.

Dependencies and integration: consumed by `If` tests for slice truthiness.

Risks and test signals: catches changes that treat empty slices as true or alter zero-result preservation.
