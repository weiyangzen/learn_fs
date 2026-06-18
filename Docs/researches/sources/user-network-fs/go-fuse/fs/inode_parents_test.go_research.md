# sources/user-network-fs/go-fuse/fs/inode_parents_test.go

Purpose: unit tests for `inodeParents` bookkeeping.

Important test flow: starts with an empty store and verifies count zero and `all()==nil`; adds five distinct `parentData` values and checks count increments and `get` returns the last added; re-adds duplicates and verifies count remains stable while newest changes; finally checks `all` length matches expected count.

State/dependencies: pure in-memory test with local `Inode` values; no FUSE mount.

Risks/test signals: covers add/newest/count/all behavior but not deletion, clear, or nondeterministic promotion after deleting newest. It is a fast regression test for hard-link parent tracking basics.
