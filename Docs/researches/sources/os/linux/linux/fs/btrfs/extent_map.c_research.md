# File Research: sources/os/linux/linux/fs/btrfs/extent_map.c

Read completely: 1396 lines.

This file implements the Btrfs in-memory extent-map cache for inode file ranges. Extent maps translate logical file offsets to disk bytenrs, holes, inline extents, prealloc extents, compression state, generation, and fast-fsync tracking state. The cache is stored as an rb-tree per inode, with a modified-extents list and an asynchronous filesystem-wide shrinker.

Core cache management:
- Creates and destroys the `btrfs_extent_map` slab cache.
- Initializes each `extent_map_tree` with an rb-root, modified list, and rwlock.
- Allocates/free extent maps with refcounting and sanity checks that freed maps are not still in the rb-tree or modified list.
- Inserts non-overlapping maps with `tree_insert()` and finds exact or nearby maps with `tree_search()`/`lookup_extent_mapping()`.
- Exposes strict lookup through `btrfs_lookup_extent_mapping()` and nearby lookup through `btrfs_search_extent_mapping()`.

Merging and validation:
- Prevents merging maps that are pinned, compressed, being logged, or still in the modified-extents list.
- Merges adjacent maps only when logical ranges, physical ranges or hole/inline markers, and flags are compatible.
- Handles merged physical extent metadata by recomputing disk bytenr, disk length, offset, and ram bytes.
- Tracks `EXTENT_FLAG_MERGED` as an in-memory-only flag.
- Performs debug-only validation of alignment and physical/ram/offset invariants.

Insertion and replacement:
- `btrfs_add_extent_mapping()` inserts a new map and handles `-EEXIST` by returning an existing covering map or trimming the new map into the gap between neighbors.
- `btrfs_replace_extent_map_range()` drops all intersecting maps and inserts a replacement, retrying if concurrent partial coverage caused another `-EEXIST`.
- `replace_extent_mapping()` swaps one rb-tree node for another while preserving modified-list semantics as requested.
- `btrfs_remove_extent_mapping()` removes a map without dropping caller-held references.

Dropping and splitting ranges:
- `btrfs_drop_extent_map_range()` removes maps intersecting an inclusive range.
- Partially overlapping maps are split into left/right remainders when spare extent maps are available.
- If split allocation fails, it removes the whole intersecting map; if that map was modified, it marks the inode for full fsync so fast fsync does not miss new extents.
- `drop_all_extent_maps_fast()` handles whole-file removal without repeated tree searches.
- `btrfs_split_extent_map()` splits a pinned modified ordered extent map into pre/mid maps when an ordered extent must be split.

Pinned/logging state:
- `btrfs_unpin_extent_cache()` clears `EXTENT_FLAG_PINNED`, sets the persisted generation, and attempts merging.
- `btrfs_clear_em_logging()` clears `EXTENT_FLAG_LOGGING` and attempts merging if the map is in the tree.
- Modified extents remain on `tree->modified_extents` for fast fsync tracking until safe removal or full-sync fallback.

Shrinker:
- Tracks evictable extent maps with `fs_info->evictable_extent_maps` for real filesystem trees.
- `btrfs_free_extent_maps()` queues asynchronous reclaim work once per pending scan request.
- The shrinker walks filesystem roots and inode xarrays, using trylocks to avoid blocking active I/O.
- `btrfs_scan_inode()` removes unpinned maps, sets full-sync on inodes when removing recent modified extents, and observes reschedule/lock-break/filesystem-closing conditions.
- Progress resumes from `em_shrinker_last_root` and `em_shrinker_last_ino`.

Important interactions:
- Used by `extent_io.c` data read/write to map file offsets to holes, inline extents, compressed extents, and disk sectors.
- Used by inode and ordered-extent code to pin newly allocated extents until ordered completion and to preserve fast-fsync correctness.
- Coordinates with `btrfs_inode::io_tree` range locks; callers dropping ranges are expected to lock relevant file ranges first.
- Uses Btrfs root/inode generation and modified-list state to decide whether cache eviction can preserve fast-fsync behavior.

Risk and correctness notes:
- The rb-tree contains non-overlapping logical ranges; all insertion/split/merge code protects that invariant.
- Extent maps may represent merged ranges that no longer correspond one-to-one with on-disk file extent items.
- Removing modified maps can cause missed fast-fsync logging unless the inode is forced to full sync; this file contains several safeguards for that.
- Shrinker code intentionally uses trylocks and asynchronous work to avoid reclaim paths blocking filesystem I/O.
- Compressed extents are not merged because physical size and decompressed offset semantics matter to read submission.
