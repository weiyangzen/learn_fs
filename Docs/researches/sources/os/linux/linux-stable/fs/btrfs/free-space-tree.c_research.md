# File Research: sources/os/linux/linux-stable/fs/btrfs/free-space-tree.c

## Purpose

Implements the on-disk free-space tree feature, which stores block-group free space in a B-tree rather than v1 cache inodes. It supports extent and bitmap item formats, conversion between them, free-space add/remove hooks, tree creation/deletion/rebuild, block-group add/remove records, loading into the runtime cache, and cleanup of orphaned free-space tree entries.

## On-Disk Model

Each block group has a `BTRFS_FREE_SPACE_INFO_KEY` item keyed by block-group start and length. Free ranges are represented either as `BTRFS_FREE_SPACE_EXTENT_KEY` items, where key objectid is start and key offset is length, or as `BTRFS_FREE_SPACE_BITMAP_KEY` items containing little-endian bitmaps. `BTRFS_FREE_SPACE_USING_BITMAPS` in the info item selects the representation for a block group.

`btrfs_free_space_root()` returns the free-space root. For extent tree v2 it uses `block_group->global_root_id` as the global root key offset; otherwise it uses the default free-space tree root.

## Format Switching

`btrfs_set_free_space_tree_thresholds()` computes high/low thresholds for converting between extents and bitmaps based on block-group length, sectorsize, and `BTRFS_FREE_SPACE_BITMAP_BITS`. `update_free_space_extent_count()` updates the info item extent count and triggers conversion:

- `btrfs_convert_free_space_to_bitmaps()` walks existing extent items backwards, builds a memory bitmap, deletes extents, marks the info item as bitmap-backed, validates the counted extents, and inserts bitmap items.
- `btrfs_convert_free_space_to_extents()` reads bitmap items into a memory bitmap, deletes bitmaps, clears the bitmap flag, emits extent keys for contiguous set bits, and validates the resulting extent count.

Memory bitmap allocation uses `memalloc_nofs_save()` around `kvzalloc()` because callers hold transactions and must avoid filesystem recursion.

## Add And Remove Paths

`btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()` are feature-gated wrappers. They look up the containing block group, lock `block_group->free_space_lock`, ensure pending block groups have their initial free-space records, and dispatch to extent or bitmap implementations based on `using_bitmaps()`.

Extent mode:

- `add_free_space_extent()` merges immediate left/right neighbors and adjusts extent count.
- `remove_free_space_extent()` handles full deletion, trimming from front/back, and middle split cases.

Bitmap mode:

- `modify_free_space_bitmap()` finds affected bitmap items, sets or clears bits across bitmap boundaries, checks adjacent bits before/after the modified range, and computes the resulting extent-count delta.
- `free_space_modify_bits()`, `free_space_next_bitmap()`, and `btrfs_free_space_test_bit()` are the low-level bitmap cursor helpers.

Errors in these transactional paths generally abort the transaction because free-space tree mismatch would corrupt allocator metadata.

## Tree Lifecycle

`btrfs_create_free_space_tree()` creates the free-space tree root, marks the tree untrusted during construction, populates each block group by walking the extent tree, sets `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID`, commits, and then clears the untrusted flag. `populate_free_space_tree()` adds the free-space info item and fills gaps between extent/metadata items found in the extent tree.

`btrfs_delete_free_space_tree()` clears feature flags, deletes all free-space tree items, deletes the root item, removes it from the global root tree, frees the root block, and commits.

`btrfs_rebuild_free_space_tree()` clears and repopulates an existing tree, allowing transaction restarts. New block groups created during rebuild are marked so the rebuild pass can skip already-added groups.

## Block-Group Hooks

`btrfs_add_block_group_free_space()` adds initial free-space records for new block groups if the feature is enabled. `__add_block_group_free_space()` handles `BLOCK_GROUP_FLAG_NEEDS_FREE_SPACE` and marks `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` to avoid rebuild duplication. `btrfs_remove_block_group_free_space()` walks backward through all free-space tree items for a block group and deletes info/extent/bitmap entries.

## Loading Runtime Cache

`btrfs_load_free_space_tree()` reads the info item using commit-root/no-lock path settings and then loads either extents or bitmaps into the in-memory block-group free-space cache with `btrfs_add_new_free_space()`. The bitmap loader reconstructs contiguous ranges by scanning sectorsize-granular bits and validates the reconstructed extent count. Both loaders periodically wake waiters after enough space is found.

## Orphan Cleanup

`btrfs_delete_orphan_free_space_entries()` removes entries before the first block group for non-extent-tree-v2 filesystems. This handles stale free-space tree entries that may predate the first valid block group. The helper starts a transaction, deletes leading items, and logs successful cleanup.

## Concurrency And Trust

The free-space tree is modified under transactions and `block_group->free_space_lock`. During creation/rebuild, `BTRFS_FS_CREATING_FREE_SPACE_TREE` and `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED` prevent consumers from trusting partially built data. Loading uses commit-root traversal to avoid deadlocks similar to block-group caching.

## Test Hooks

Several functions are exported under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`: add/remove internals, format conversion helpers, and bitmap bit testing. These provide direct coverage of format transitions and range modifications.
