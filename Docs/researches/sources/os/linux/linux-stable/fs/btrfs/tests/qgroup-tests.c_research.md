# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/qgroup-tests.c

## Role

Self-test coverage for Btrfs qgroup extent accounting using an in-memory dummy filesystem. The file manually creates and removes extent items/backrefs, walks roots through `btrfs_find_all_roots()`, and calls `btrfs_qgroup_account_extent()` directly because the dummy transaction does not model full delayed-ref machinery.

## Main Entry Point

- `btrfs_test_qgroups(sectorsize, nodesize)`: allocates dummy `fs_info`, extent root, quota root, and two fs roots, enables `BTRFS_FS_QUOTA_ENABLED`, then runs the qgroup scenarios.

## Helpers

- `insert_normal_tree_ref()`: inserts an `EXTENT_ITEM` with one inline tree block ref, either `TREE_BLOCK_REF` for root-owned refs or `SHARED_BLOCK_REF` for parent refs.
- `add_tree_ref()`: increments the extent ref count and inserts a keyed tree/shared block ref item.
- `remove_extent_item()`: deletes the whole extent item.
- `remove_extent_ref()`: decrements the extent ref count and removes the keyed backref.

## Test Scenarios

- `test_no_shared_qgroup()`: creates qgroup for `BTRFS_FS_TREE_OBJECTID`, verifies adding one tree block charges referenced and exclusive bytes, then deleting it returns both counts to zero.
- `test_multiple_refs()`: creates a second qgroup, adds a second root ref to the same extent, verifies both qgroups become referenced but not exclusive, then removes one ref and verifies exclusivity returns to the remaining owner.

## Dependencies and Interactions

- Exercises qgroup APIs from `qgroup.h`, root discovery from `backref.h`, and item manipulation through ctree accessors.
- Uses `btrfs_init_dummy_trans()` rather than normal transaction start/commit.
- Relies on dummy roots inserted with `btrfs_insert_fs_root()` so backref walking can resolve root IDs.

## Error Handling Notes

- Allocation/search/insert failures log via self-test helpers and return kernel errno values.
- The test depends on `btrfs_qgroup_account_extent()` consuming/freeing old/new root ulists after successful accounting.
- The test intentionally avoids bytenr zero because backref walking expects nonzero block addresses.
