# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/qgroup-tests.c

## Summary
Selftests Btrfs qgroup accounting by building dummy extent-tree state, walking backrefs, and calling `btrfs_qgroup_account_extent()` directly for controlled add/remove scenarios.

## Main Responsibilities
- Create synthetic extent items and inline/tree backrefs in a dummy extent tree.
- Add and remove tree refs while manually updating extent ref counts.
- Use `btrfs_find_all_roots()` to compute old/new root ownership sets.
- Verify qgroup referenced/exclusive counts after extent ownership changes.
- Set up dummy fs roots for `BTRFS_FS_TREE_OBJECTID` and `BTRFS_FIRST_FREE_OBJECTID`.

## Key APIs
- Test entry: `btrfs_test_qgroups()`.
- Helpers: `insert_normal_tree_ref()`, `add_tree_ref()`, `remove_extent_item()`, `remove_extent_ref()`.
- Test cases: `test_no_shared_qgroup()`, `test_multiple_refs()`.
- Btrfs APIs under test: `btrfs_create_qgroup()`, `btrfs_find_all_roots()`, `btrfs_qgroup_account_extent()`, `btrfs_verify_qgroup_counts()`.

## Important Behavior
`test_no_shared_qgroup()` creates one qgroup, inserts a tree ref for one root, accounts the extent, expects referenced and exclusive bytes to equal `nodesize`, then removes the extent item and expects both counters to return to zero.

`test_multiple_refs()` creates a second qgroup/root, first accounts a single-root extent, then adds a second root reference. Both qgroups should report referenced bytes but zero exclusive bytes while the extent is shared. Removing the second ref should drop that qgroup to zero and restore exclusivity to the first root.

The test bypasses normal delayed refs because dummy transactions do not model the full kernel delayed-ref machinery. It directly computes old/new root lists and passes them to qgroup accounting.

## Setup and State
The entry point allocates dummy `fs_info` and an extent root, inserts it as a global extent-tree root, points `tree_root` and `quota_root` at it, enables `BTRFS_FS_QUOTA_ENABLED`, allocates an extent buffer at `nodesize`, and inserts two dummy fs roots into `fs_roots_radix`.

## Risks
These tests depend on precise dummy tree shape and bytenr choices. Bytenr `0` is intentionally avoided because backref walking assumes real nonzero block addresses. The tests also depend on `btrfs_qgroup_account_extent()` freeing the ulists passed into it.
