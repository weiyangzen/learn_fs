# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/qgroup-tests.c

## Purpose

This file implements Btrfs selftests for qgroup accounting behavior using dummy filesystem/root objects and synthetic extent-tree backreferences. It verifies that `btrfs_qgroup_account_extent()` updates referenced and exclusive byte counters correctly when tree block references are added, shared between roots, and removed.

## Main Entry Point

- `btrfs_test_qgroups(u32 sectorsize, u32 nodesize)`: constructs a dummy `fs_info`, dummy extent root, quota root, and two filesystem roots, then runs:
  - `test_no_shared_qgroup()`
  - `test_multiple_refs()`

## Helpers

- `insert_normal_tree_ref()`: inserts a synthetic `BTRFS_EXTENT_ITEM_KEY` with one inline tree block reference. It can create either:
  - `BTRFS_TREE_BLOCK_REF_KEY` when `parent == 0`
  - `BTRFS_SHARED_BLOCK_REF_KEY` when `parent > 0`
- `add_tree_ref()`: increments extent refcount and inserts a separate keyed backref item.
- `remove_extent_item()`: deletes the whole extent item.
- `remove_extent_ref()`: decrements extent refcount and deletes the matching keyed backref.

All helpers use `btrfs_init_dummy_trans()` and explicit B-tree path allocation, so they exercise real B-tree item insertion/search/deletion paths without a mounted filesystem.

## Test Scenarios

`test_no_shared_qgroup()`:
- Creates qgroup for `BTRFS_FS_TREE_OBJECTID`.
- Captures old roots for the target bytenr with `btrfs_find_all_roots()`.
- Inserts a single tree block ref owned by the filesystem tree.
- Captures new roots and accounts the extent.
- Verifies qgroup referenced/exclusive counts become `nodesize/nodesize`.
- Removes the extent item.
- Accounts again and verifies counts return to zero.

`test_multiple_refs()`:
- Creates qgroup for `BTRFS_FIRST_FREE_OBJECTID`.
- Inserts one tree ref for `BTRFS_FS_TREE_OBJECTID` and verifies it is fully exclusive.
- Adds another tree ref for `BTRFS_FIRST_FREE_OBJECTID`.
- Verifies both roots reference the bytes but neither has exclusive bytes.
- Removes the second root’s ref.
- Verifies first root returns to exclusive ownership and second root returns to zero.

## Dependencies and Integration

This selftest depends on Btrfs core internals:
- Extent item format from `ctree.h` and accessors.
- Dummy transaction/root/fs helpers from the Btrfs selftest harness.
- Backref walking through `btrfs_find_all_roots()`.
- Qgroup APIs from `qgroup.h`.
- Global root insertion and dummy fs root lookup behavior.

`btrfs_test_qgroups()` is expected to be called by the Btrfs selftest runner with chosen sector/node sizes.

## Important Invariants

- The dummy extent root doubles as `tree_root` and `quota_root` to satisfy code paths that assume populated `fs_info`.
- `BTRFS_FS_QUOTA_ENABLED` is set before qgroup accounting.
- Dummy roots are inserted into the fs root radix/tree so backref walking can resolve root ownership.
- The tested extent bytenr is `nodesize`, not zero, because backref walking paths do not tolerate bytenr zero.
- `btrfs_qgroup_account_extent()` consumes/frees the old/new root ulists passed to it; the test resets local pointers after calls.

## Error Handling

The file reports failures through `test_err()` / `test_std_err()` and returns negative errno values. Allocation failure returns `-ENOMEM`; logic/accounting mismatch generally returns `-EINVAL`.

## Research Notes

This is a focused qgroup regression test rather than a generic qgroup harness. It directly edits extent-tree items and then invokes the same accounting and backref resolution functions used by production code, making it useful for catching regressions in qgroup root-difference accounting and backref interpretation.
