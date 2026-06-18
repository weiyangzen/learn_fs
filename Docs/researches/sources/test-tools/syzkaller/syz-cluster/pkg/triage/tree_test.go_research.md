## sources/test-tools/syzkaller/syz-cluster/pkg/triage/tree_test.go

`tree_test.go` validates pure tree helper behavior. `TestSelectTrees` covers single subsystem match, configured-order preservation across multiple matches, fallback to mainline, and subject-tag priority over Cc-derived trees. `TestTreeFromBranch` validates parsing `tree/branch` references. `TestFindTreeByName` validates successful and missing name lookup.

These tests are concise and deterministic. They do not cover case-insensitive configured email lists or duplicate tree names, but they provide the core signal for triage ordering semantics.
