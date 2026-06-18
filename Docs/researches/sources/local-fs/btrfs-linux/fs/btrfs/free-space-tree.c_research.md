# File Research: sources/local-fs/btrfs-linux/fs/btrfs/free-space-tree.c

## Summary
Implements the persistent Btrfs free-space tree, the compat-ro replacement for free-space cache v1. It stores per-block-group free-space information in B-tree items, switches between extent keys and bitmap items, updates the tree during allocation/free operations, loads free space into the in-memory block-group cache, and creates, deletes, or rebuilds the tree.

## Main Responsibilities
- Select the correct free-space root, including extent-tree-v2 per-global-root handling.
- Create and find per-block-group `BTRFS_FREE_SPACE_INFO_KEY` items.
- Maintain extent count and bitmap-format flags for each block group.
- Convert block-group free-space representation between extent items and bitmap items.
- Add and remove free-space ranges in extent or bitmap representation.
- Populate the free-space tree by scanning extent-tree metadata.
- Create, delete, rebuild, and clear the free-space tree.
- Add or remove all free-space items for a block group.
- Load free-space tree contents into the in-memory free-space cache during block-group caching.
- Delete orphan free-space entries that precede the first real block group.

## Key APIs
- Root and threshold helpers: `btrfs_free_space_root()`, `btrfs_set_free_space_tree_thresholds()`, `btrfs_search_free_space_info()`.
- Feature lifecycle: `btrfs_create_free_space_tree()`, `btrfs_delete_free_space_tree()`, `btrfs_rebuild_free_space_tree()`.
- Block-group lifecycle: `btrfs_add_block_group_free_space()`, `btrfs_remove_block_group_free_space()`.
- Range updates: `btrfs_add_to_free_space_tree()`, `btrfs_remove_from_free_space_tree()`.
- Loading and repair: `btrfs_load_free_space_tree()`, `btrfs_delete_orphan_free_space_entries()`.
- Test-exported internals: `__btrfs_add_to_free_space_tree()`, `__btrfs_remove_from_free_space_tree()`, `btrfs_convert_free_space_to_bitmaps()`, `btrfs_convert_free_space_to_extents()`, `btrfs_free_space_test_bit()`.

## Important Behavior
Each block group has an info item keyed by block-group start and length. Free-space payload is stored after the info item as either `BTRFS_FREE_SPACE_EXTENT_KEY` items, where key offset is extent length, or `BTRFS_FREE_SPACE_BITMAP_KEY` items containing little-endian bitmap data. The info item records extent count and the `BTRFS_FREE_SPACE_USING_BITMAPS` flag.

Thresholds compare estimated metadata space for extent items with bitmap item space. When extent count rises above `bitmap_high_thresh`, extents are converted into bitmap items. When count drops below `bitmap_low_thresh`, bitmaps are converted back into extents. The gap between thresholds prevents format thrashing.

Extent-mode removal finds the containing extent key and handles four split cases: full removal, trim from beginning, trim from end, or split into two leftovers. Extent-mode addition searches adjacent left and right neighbors and merges if contiguous before inserting the resulting key.

Bitmap-mode updates locate the bitmap before or containing the target range, set or clear bits across one or more bitmap items, inspect neighboring bits, and adjust the logical extent count by whether the operation merged or split free extents.

Creation builds a new free-space tree root, marks the tree untrusted during population, walks every block group, scans the extent tree for allocated extent and metadata items, and inserts free gaps into the free-space tree. Only after commit is the free-space tree considered trusted for block-group caching.

Rebuild clears the existing tree, repopulates block groups, and handles new block groups created during rebuild by marking `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` so they are not populated twice.

Loading starts from the block group's info item using the commit root with locking skipped, then either iterates free-space extent keys or reconstructs extents from bitmap bits. Found ranges are added to the in-memory free-space cache via `btrfs_add_new_free_space()`, with wakeups after enough space has been discovered.

## State and Synchronization
`block_group->free_space_lock` serializes modifications for one block group. Path objects are reused carefully and released between insertions/deletions to avoid stale leaf state after tree changes.

The create/rebuild paths set `BTRFS_FS_CREATING_FREE_SPACE_TREE` and `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED` to prevent consumers from trusting incomplete state. Compat-ro feature bits `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID` gate public add/remove/load operations.

Allocation inside tree modification uses NOFS for bitmap buffers because callers hold transaction handles and must not recurse into filesystem allocation or transaction commit paths.

## Risks
Extent count is a central invariant. Conversion and bitmap updates verify counted extents against the info item; mismatches produce errors and transaction aborts because they imply free-space tree corruption.

The code relies on key ordering and reverse searches for the previous slot. Unexpected key types or missing previous slots are treated as corruption or logic errors.

Free-space tree creation and rebuild modify free-space metadata while normal extent allocation hooks may also update the same tree. The `NEEDS_FREE_SPACE` and `FREE_SPACE_ADDED` runtime flags are critical to avoiding duplicate block-group entries.

Bitmap operations use little-endian bit order in extent buffers and must correctly account for block-group boundaries, partial final bitmaps, and adjacent bits across bitmap item boundaries.
