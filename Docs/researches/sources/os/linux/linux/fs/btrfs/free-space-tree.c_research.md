# File Research: sources/os/linux/linux/fs/btrfs/free-space-tree.c

## Purpose
Implements Btrfs free-space tree support. Unlike free-space cache v1, the free-space tree stores free-space metadata directly in Btrfs trees using free-space info, extent, and bitmap items. It supports creation, deletion, rebuild, incremental add/remove updates, block-group add/remove, and loading tree contents into block-group in-memory free-space caches.

## Main On-Disk Model
For each block group:
- `BTRFS_FREE_SPACE_INFO_KEY`: one info item keyed by block-group start and length; stores extent count and flags.
- `BTRFS_FREE_SPACE_EXTENT_KEY`: extent-format free range; `objectid=start`, `offset=size`.
- `BTRFS_FREE_SPACE_BITMAP_KEY`: bitmap-format free range; `objectid=bitmap_start`, `offset=covered_bytes`, payload bitmap.

`btrfs_free_space_root()` selects the global free-space tree root. With `EXTENT_TREE_V2`, it uses the block group’s `global_root_id`.

## Thresholds and Format Conversion
- `btrfs_set_free_space_tree_thresholds()` calculates bitmap high/low thresholds from block-group length, sectorsize, bitmap item size, and item overhead.
- `update_free_space_extent_count()` updates extent count in the info item and converts representation when thresholds are crossed.
- `btrfs_convert_free_space_to_bitmaps()` walks existing free-space extent items, builds a little-endian bitmap, deletes extent items, sets `BTRFS_FREE_SPACE_USING_BITMAPS`, then inserts bitmap items.
- `btrfs_convert_free_space_to_extents()` reads bitmap items into memory, deletes bitmap items, clears the bitmap flag, and emits extent items for each contiguous set-bit run.

## Bitmap Helpers
- `free_space_bitmap_size()` computes bytes required to represent a byte range at filesystem sectorsize granularity.
- `alloc_bitmap()` uses `memalloc_nofs_save()` around `kvzalloc()` to avoid filesystem recursion while holding transactions.
- `le_bitmap_set()` explicitly writes little-endian bitmap bits.
- `btrfs_free_space_test_bit()` tests an on-disk bitmap item bit.
- `free_space_modify_bits()` sets or clears bits in an extent buffer and advances the caller’s range.
- `free_space_next_bitmap()` moves to the next writable bitmap item without relying on read-only tree walking.
- `modify_free_space_bitmap()` mutates bitmap-backed free space and adjusts extent count based on neighbor bits before/after the changed range.

## Extent Helpers
- `add_free_space_extent()` merges new free space with immediate left/right extent neighbors, then inserts one combined extent key and updates extent count.
- `remove_free_space_extent()` splits or deletes an existing free-space extent according to four cases:
  - full extent removal,
  - removing from the beginning,
  - removing from the end,
  - removing from the middle into two leftover extents.
- `btrfs_search_prev_slot()` wraps `btrfs_search_slot()` for “greatest key less than target” lookups and asserts expected non-exact search behavior.
- `using_bitmaps()` caches a block group’s free-space-tree representation state.

## Public Add/Remove Hooks
- `btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()` are transaction hooks for free-space changes.
- They no-op when `FREE_SPACE_TREE` compat-ro feature is absent.
- Both allocate a path, locate the block group, take `block_group->free_space_lock`, dispatch to extent or bitmap mutation, abort the transaction on error, and drop the block-group reference.
- Test-visible internal variants `__btrfs_add_to_free_space_tree()` and `__btrfs_remove_from_free_space_tree()` accept a known block group and path.

## Tree Creation, Deletion, and Rebuild
- `populate_free_space_tree()` scans the extent tree for allocated extents/metadata items in a block group and inserts gaps into the free-space tree.
- `btrfs_create_free_space_tree()` creates the free-space tree root, populates all block groups, sets `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID`, and clears the untrusted flag after commit.
- `clear_free_space_tree()` deletes all free-space tree items and clears per-block-group `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED`.
- `btrfs_delete_free_space_tree()` clears feature flags, deletes all items, removes the root item/global root, frees the root node, and commits.
- `btrfs_rebuild_free_space_tree()` clears and repopulates the tree, possibly across multiple transactions, while marking the tree untrusted until committed.

## Block Group Integration
- `__add_block_group_free_space()` lazily initializes a new block group’s free-space info item and full-block-group free extent when `BLOCK_GROUP_FLAG_NEEDS_FREE_SPACE` is set.
- `btrfs_add_block_group_free_space()` exposes this for block group creation.
- `btrfs_remove_block_group_free_space()` deletes all free-space tree items belonging to a block group.
- Rebuild logic uses `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` to avoid double-populating block groups created during rebuild transactions.

## Loading Into In-Memory Cache
- `btrfs_load_free_space_tree()` starts from the block group’s info item in the committed free-space tree and dispatches by representation flag.
- `load_free_space_extents()` iterates extent items and calls `btrfs_add_new_free_space()`.
- `load_free_space_bitmaps()` scans bitmap bits into contiguous ranges and calls `btrfs_add_new_free_space()`.
- Both validate observed extent count against the info item and wake the caching waitqueue after sufficient progress.

## Orphan Cleanup
- `btrfs_delete_orphan_free_space_entries()` removes free-space tree items that appear before the first block group, skipping `EXTENT_TREE_V2` because that mode uses multiple global roots.

## Concurrency and Integrity
- Per-block-group free-space tree mutations are serialized by `block_group->free_space_lock`.
- Tree operations run under a transaction and abort on structural errors.
- `BTRFS_FS_CREATING_FREE_SPACE_TREE` and `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED` coordinate creation/rebuild state with cache users.
- The file uses extensive assertions to validate item key ranges, expected key types, and extent count consistency.
