# File Research: sources/os/linux/linux-stable/fs/btrfs/extent_map.c

## Purpose

`extent_map.c` implements Btrfs' in-memory extent map cache for file extents. Extent maps describe logical file ranges and their backing disk ranges, holes, inline extents, compression state, preallocation, pinning, logging state, and fsync generations.

## Core Data Structure Behavior

- Extent maps live in an inode-local red-black tree (`extent_map_tree.root`) protected by an rwlock.
- Modified extents are tracked on `extent_map_tree.modified_extents` for fast fsync.
- Each map is refcounted. Tree insertion takes a reference; lookups take a reference; removals and callers drop references separately.
- `btrfs_extent_map_init()` and `btrfs_extent_map_exit()` manage the slab cache.

## Lookup and Insertion

- `tree_insert()` rejects overlapping ranges and validates neighbor overlap.
- `tree_search()` finds either an intersecting extent or a neighboring extent.
- `btrfs_lookup_extent_mapping()` returns the first intersecting map.
- `btrfs_search_extent_mapping()` may return a nearby map even if it does not strictly intersect, used when resolving insertion races.
- `btrfs_add_extent_mapping()` inserts a new map or handles `-EEXIST` by returning the existing map or fitting the new map between neighbors through `merge_extent_mapping()`.

## Merging

- `can_merge_extent_map()` rejects pinned, compressed, logging, or modified-list maps.
- `mergeable_maps()` requires logical adjacency, compatible flags, and either physical adjacency or matching hole/inline sentinels.
- `merge_ondisk_extents()` updates physical extent fields when adjacent regular extents are merged.
- `try_merge_map()` merges with previous and next neighbors when safe and when the map is not held by other users.

## Removal and Replacement

- `btrfs_remove_extent_mapping()` removes a map from the rb-tree and modified list when appropriate.
- `replace_extent_mapping()` swaps an existing tree node with a new map while preserving modified-list semantics.
- `btrfs_drop_extent_map_range()` drops all maps intersecting a range, splitting boundary maps when memory is available.
  - If splitting fails for a modified map, it removes the whole map and marks the inode for full fsync so fast fsync will not miss new extents.
  - The fast path `drop_all_extent_maps_fast()` removes the entire tree when dropping `[0, U64_MAX]` without skipping pinned maps.
- `btrfs_replace_extent_map_range()` repeatedly drops overlapping maps and inserts a replacement until `-EEXIST` no longer occurs.

## Ordered Extent and Fsync Integration

- `btrfs_unpin_extent_cache()` clears `EXTENT_FLAG_PINNED` after writeback completion and records the generation that inserted the file item.
- `btrfs_split_extent_map()` splits a pinned modified extent map when an ordered extent is split, replacing the original with pre/mid maps and preserving modified tracking.
- `btrfs_clear_em_logging()` clears logging state and tries to merge the map.

## Shrinker

- `btrfs_free_extent_maps()` schedules asynchronous reclaim through `em_shrinker_work`.
- `btrfs_extent_map_shrinker_worker()` scans filesystem roots and inodes, removing reclaimable extent maps under memory pressure.
- `btrfs_scan_inode()` skips pinned maps, sets full-sync when removing recent modified maps, and stops on scheduling/lock contention or filesystem closing.
- `find_first_inode_to_shrink()` avoids blocking on busy extent-map locks and skips inodes with empty trees.

## Correctness Notes

- Extent maps can be merged and therefore do not always correspond one-to-one to on-disk file extent items.
- Compressed extents are deliberately not merged because their physical size matters.
- Removal of modified extents is tied to fsync correctness. If an extent needed for fast fsync could be lost, the inode is forced to full sync.
- The code validates alignment and physical fields in debug builds via `validate_extent_map()`.
