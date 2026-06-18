# File Research: sources/local-fs/kdave-linux/fs/btrfs/free-space-tree.c

This file implements Btrfs free-space tree support: a persistent tree alternative to the v1 free-space cache inode. It records free regions per block group as either extent items or bitmap items, supports conversion between the formats, and can create, rebuild, delete, update, and load the tree.

Major responsibilities:
- Selects the correct free-space tree root for a block group, including extent-tree-v2 global root selection by `global_root_id`.
- Creates the per-block-group `BTRFS_FREE_SPACE_INFO_KEY` item and maintains its free extent count and bitmap-format flag.
- Adds and removes free-space ranges from the persistent tree during extent allocation/freeing.
- Converts a block group representation between individual `BTRFS_FREE_SPACE_EXTENT_KEY` items and `BTRFS_FREE_SPACE_BITMAP_KEY` items when thresholds are crossed.
- Builds or rebuilds the free-space tree by scanning allocated extents in the extent tree.
- Loads the free-space tree into a block group's in-memory free-space cache during block group caching.
- Deletes orphan free-space tree entries that precede the first block group.

Tree format:
- Each block group has one info item keyed as `(block_group->start, BTRFS_FREE_SPACE_INFO_KEY, block_group->length)`.
- Extent representation stores one empty item per free range with key objectid equal to range start and offset equal to length.
- Bitmap representation stores bitmap items where bits correspond to sectorsize units; default bitmap data size is `BTRFS_FREE_SPACE_BITMAP_SIZE` bytes.
- `BTRFS_FREE_SPACE_USING_BITMAPS` in the info item decides whether range updates modify bitmap bits or extent items.

Threshold and conversion behavior:
- `btrfs_set_free_space_tree_thresholds()` computes high/low conversion thresholds from block group length, sectorsize, item overhead, and bitmap size.
- `update_free_space_extent_count()` adjusts the info-item extent count and converts to bitmaps above the high threshold or back to extents below the low threshold.
- `btrfs_convert_free_space_to_bitmaps()` walks extent items backward, sets little-endian bitmap bits, deletes extent items, sets the bitmap flag, verifies expected extent count, then inserts bitmap items.
- `btrfs_convert_free_space_to_extents()` reads bitmap items into memory, deletes them, clears the bitmap flag, scans set bits into extent items, and verifies the extent count.
- `alloc_bitmap()` uses a NOFS section around `kvzalloc()` because all callers hold transaction handles and filesystem recursion could deadlock.

Range update flow:
- Public `btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()` no-op unless the `FREE_SPACE_TREE` compat-ro feature is enabled.
- Both locate the containing block group, take `block_group->free_space_lock`, ensure delayed new-block-group free space is materialized via `__add_block_group_free_space()`, then update either bitmap or extent representation.
- Extent add merges immediate left/right neighbors and updates the count according to whether one, two, or no neighbors were absorbed.
- Extent remove splits the containing free extent into zero, one, or two leftovers and updates the count accordingly.
- Bitmap add/remove uses `modify_free_space_bitmap()` to set or clear bits across one or more bitmap items and adjusts extent count based on neighbor bits at both edges.

Free-space tree lifecycle:
- `btrfs_create_free_space_tree()` creates the free-space tree root, marks it untrusted while populating, populates every block group, sets `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID`, commits, then clears the untrusted flag.
- `btrfs_delete_free_space_tree()` clears the feature bits, removes all items, deletes the root item, detaches the root from global root tracking, clears its dirty state, frees the root block, and commits.
- `btrfs_rebuild_free_space_tree()` clears existing entries, repopulates all eligible block groups across one or more transactions, marks new block groups already added during rebuild so they are not populated twice, then validates feature bits on commit.
- `clear_free_space_tree()` also clears `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` on all block groups after deleting tree items.

Population and loading:
- `populate_free_space_tree()` inserts the info item, scans extent or metadata items in the extent tree for a block group, and records gaps between allocated extents as free space.
- It handles extent-tree-v2/block-group-tree cases where empty block groups may not have a block group item in the extent tree.
- `btrfs_load_free_space_tree()` reads the committed free-space tree with `search_commit_root`, `skip_locking`, and forward readahead to avoid deadlocks during caching.
- `load_free_space_extents()` adds each free-space extent item into the live block group cache with `btrfs_add_new_free_space()` and wakes waiters after enough progress.
- `load_free_space_bitmaps()` scans bitmap bits into contiguous free ranges, adds them to the live cache, and verifies the reconstructed extent count.

Block group insertion/removal:
- `btrfs_add_block_group_free_space()` adds an info item and initially marks the whole new block group free when the free-space tree feature is active.
- `__add_block_group_free_space()` is guarded by `BLOCK_GROUP_FLAG_NEEDS_FREE_SPACE` and sets `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` to coordinate rebuilds with block groups created mid-rebuild.
- `btrfs_remove_block_group_free_space()` walks backward through all free-space extent/bitmap/info items for the block group and deletes them, unless the block group was never added.

Consistency and error handling:
- Unexpected free-space tree key types are treated as corruption (`-EUCLEAN`) and abort the transaction.
- Count mismatches between info-item extent count and reconstructed extents return errors and abort where inside a transaction.
- Add/remove wrappers abort the transaction on update failures.
- `btrfs_delete_orphan_free_space_entries()` ignores extent-tree-v2, checks the first block group bytenr, and deletes free-space tree items before it.

Concurrency:
- `block_group->free_space_lock` serializes persistent free-space tree updates per block group.
- Path operations that modify tree items require COW and are transaction-bound.
- Loading from the tree intentionally avoids normal locking against current tree modifications by reading from the commit root.
