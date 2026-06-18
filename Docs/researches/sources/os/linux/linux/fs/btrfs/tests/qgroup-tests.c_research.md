# File Research: sources/os/linux/linux/fs/btrfs/tests/qgroup-tests.c

## Purpose

This file implements Btrfs selftests for qgroup accounting using dummy filesystem/root objects and synthetic extent-tree backreferences. It verifies that `btrfs_qgroup_account_extent()` updates referenced and exclusive byte counters correctly when a tree block becomes owned, shared between roots, and unshared/removed.

## Main Entry Point

- `btrfs_test_qgroups(u32 sectorsize, u32 nodesize)`: creates a dummy `fs_info`, an extent/quota/tree root, and two dummy fs roots, enables `BTRFS_FS_QUOTA_ENABLED`, then runs:
  - `test_no_shared_qgroup()`
  - `test_multiple_refs()`

## Helper Functions

- `insert_normal_tree_ref()`: inserts a synthetic `BTRFS_EXTENT_ITEM_KEY` containing one inline tree block reference. It writes the extent item, tree block info, and inline ref directly into the leaf.
- `add_tree_ref()`: increments the extent refcount and inserts a keyed backref item for either `BTRFS_SHARED_BLOCK_REF_KEY` or `BTRFS_TREE_BLOCK_REF_KEY`.
- `remove_extent_item()`: removes the whole extent item from the dummy extent tree.
- `remove_extent_ref()`: decrements the extent refcount and deletes the matching keyed backref item.

All helpers use `btrfs_init_dummy_trans()` and real B-tree search/insert/delete helpers, so the test exercises actual metadata manipulation paths in a minimal harness.

## Test Scenarios

`test_no_shared_qgroup()`:
- Creates a qgroup for `BTRFS_FS_TREE_OBJECTID`.
- Captures old roots for `nodesize` with `btrfs_find_all_roots()`.
- Inserts a single tree block ref owned by the filesystem tree.
- Captures new roots and calls `btrfs_qgroup_account_extent()`.
- Verifies referenced/exclusive counts become `nodesize/nodesize`.
- Removes the extent item, accounts again, and verifies counts return to zero.

`test_multiple_refs()`:
- Creates a qgroup for `BTRFS_FIRST_FREE_OBJECTID`.
- Inserts one tree ref for `BTRFS_FS_TREE_OBJECTID` and verifies it is exclusive.
- Adds a second ref for `BTRFS_FIRST_FREE_OBJECTID`.
- Verifies both roots have referenced bytes but zero exclusive bytes.
- Removes the second ref.
- Verifies the first root returns to exclusive ownership while the second root returns to zero.

## Key Dependencies

- Backref walking: `btrfs_find_all_roots()`.
- Qgroup APIs: `btrfs_create_qgroup()`, `btrfs_qgroup_account_extent()`, `btrfs_verify_qgroup_counts()`.
- Extent item accessors and inline ref layout.
- Dummy fs/root/transaction selftest helpers.
- Global root insertion and dummy fs-root lookup behavior.

## Important Invariants

- The tested bytenr is `nodesize`, not zero, because backref walking paths do not tolerate bytenr zero.
- The dummy extent root is also assigned as `tree_root` and `quota_root`.
- Dummy fs roots are inserted so backref walking can resolve root ownership.
- `btrfs_qgroup_account_extent()` frees the old/new root ulists it receives; the test resets local pointers after successful calls.
- Qgroup accounting is called directly because the dummy transaction does not have production delayed-ref machinery.

## Error Handling

Failures are reported with `test_err()` or `test_std_err()`. Allocation failures return `-ENOMEM`; accounting mismatches and unexpected lookup/deletion behavior generally return `-EINVAL`.

## Research Notes

This is a narrow qgroup regression test. It is valuable because it drives the qgroup root-difference accounting with synthetic but structurally real extent-tree backreferences, covering both exclusive and shared ownership transitions.
