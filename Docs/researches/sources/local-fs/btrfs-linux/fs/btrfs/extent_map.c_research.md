# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent_map.c

## Scope

This file implements Btrfs in-memory file extent maps: allocation, rb-tree insertion/search/removal, merging adjacent compatible mappings, unpinning maps after ordered extent completion, replacing/dropping ranges, splitting pinned maps, and asynchronous memory-pressure reclaim. Extent maps cache file logical ranges, holes, inline extents, prealloc extents, compression state, physical disk ranges, generation, and fsync logging state.

## Main APIs And Entry Points

- `btrfs_extent_map_init()` and `btrfs_extent_map_exit()` manage the extent-map slab cache.
- `btrfs_extent_map_tree_init()` initializes an inode's extent-map tree and modified-extents list.
- `btrfs_alloc_extent_map()` and `btrfs_free_extent_map()` allocate and release refcounted extent maps.
- `btrfs_lookup_extent_mapping()` finds the first map intersecting a range.
- `btrfs_search_extent_mapping()` finds an intersecting or nearby map for conflict handling.
- `btrfs_add_extent_mapping()` inserts a new map, returning an existing map or trimming/merging on insertion races.
- `btrfs_remove_extent_mapping()` removes a map from an inode tree without dropping caller references.
- `btrfs_drop_extent_map_range()` removes all maps intersecting a range and splits partially overlapping maps when possible.
- `btrfs_replace_extent_map_range()` repeatedly drops a target range and inserts a replacement map until insertion no longer races.
- `btrfs_split_extent_map()` splits a pinned ordered extent map into pre and remaining pieces when an ordered extent is split.
- `btrfs_unpin_extent_cache()` clears PINNED after successful writeback, updates generation, and attempts merging.
- `btrfs_clear_em_logging()` clears LOGGING and attempts merging if safe.
- `btrfs_free_extent_maps()` schedules asynchronous extent-map reclaim, and `btrfs_init_extent_map_shrinker_work()` initializes that work item.

## Control Flow And Behavior

Extent maps are stored in an inode-local rb-tree keyed by file offset. `tree_insert()` rejects overlaps and double-checks neighboring nodes. `tree_search()` returns an exact containing node when possible or a nearby predecessor/successor for callers that need merge/conflict context. Lookups take an extra reference on returned maps; the tree itself owns a reference for inserted maps.

Insertion validates map alignment and physical fields in debug builds. `add_extent_mapping()` inserts directly and then either links the map into `modified_extents` or tries to merge it with neighbors. `btrfs_add_extent_mapping()` handles `-EEXIST` races from concurrent readers/writers: if the requested start falls inside an existing map, it returns that existing map to the caller; otherwise it trims the new map to the gap between neighboring maps and inserts that reduced range.

Merging is intentionally conservative. Maps cannot merge if pinned, compressed, logging, or still on the modified-extents list. `try_merge_map()` also refuses to mutate a map with more than the tree and current-task references, because another user could observe partially updated fields. Merge compatibility requires adjacent logical ranges, equal flags ignoring MERGED, and either physically adjacent regular extents or equal special disk markers for holes/inline. `merge_ondisk_extents()` updates the physical extent envelope and logical offset so maps that cover adjacent parts of one or more regular data extents remain coherent.

Pinned maps represent extents not yet fully persisted. `btrfs_unpin_extent_cache()` looks up the exact start, warns on missing or unexpected maps, records the generation that inserted the file item, clears PINNED, and then tries to merge. `btrfs_clear_em_logging()` clears LOGGING after fsync no longer needs to protect the map from merging.

Range dropping removes every map intersecting `[start, end]`. Fully covered maps are removed directly. Partially covered maps are split into left and/or right replacement maps if spare allocations are available; if splitting a modified map fails due to allocation shortage, the whole map is removed and the inode is marked for full fsync so fast fsync cannot miss new extents. Pinned maps can be skipped when requested.

`btrfs_replace_extent_map_range()` wraps range dropping plus insertion for callers that need an exact replacement, retrying on `-EEXIST` because unrelated partial maps may be inserted while the caller held only the appropriate inode IO-tree lock.

The extent-map shrinker runs asynchronously. It walks filesystem roots and inodes using remembered root/inode cursors, tries to take extent-map tree write locks without blocking, skips empty trees, and scans maps until its budget is consumed. Before removing a modified map from the current or newer fs generation, it takes `i_mmap_lock` in read mode and marks the inode full-sync, avoiding races with fast fsync's inode logging phase. Pinned maps are not reclaimed.

## State And Data Structures

- `struct extent_map` stores rb-node, file `start/len`, `disk_bytenr`, `disk_num_bytes`, decompressed `offset/ram_bytes`, `generation`, flags, refcount, and modified-extents list node.
- `struct extent_map_tree` stores the rb-tree root, modified-extents list, and rwlock.
- Flags handled here include PINNED, compression type bits, PREALLOC, LOGGING, and MERGED.
- `fs_info->evictable_extent_maps` counts reclaimable maps for normal filesystem roots.
- `fs_info->em_shrinker_nr_to_scan`, `em_shrinker_work`, `em_shrinker_last_root`, and `em_shrinker_last_ino` coordinate async shrinker progress.

## Dependencies

This file depends on inode/root/fs structures, Btrfs compression flags, fs generation, fsync full-sync marking, ordered extent semantics, testing-mode checks, root radix/inode xarray traversal, tracing hooks, and kernel rb-tree/refcount/slab primitives.

## Risks And Invariants

- Callers that mutate an extent-map tree must hold `extent_tree.lock` in write mode; lookup callers must obey the tree lock contract used by their path.
- Inserted maps carry an extra tree reference. Removal and replacement must drop the tree reference separately from lookup/caller references.
- Pinned and logging maps must not be merged or removed blindly, because ordered extent completion and fast fsync depend on their exact identity.
- Compressed maps are never merged because physical compressed size and offset semantics do not match logical contiguity.
- Removing a modified current-generation map can make fast fsync miss it; the code must mark the inode full-sync in those cases.
- Partial range-drop split allocation failure is tolerated only because the map can be reloaded from disk and full fsync is forced if logging correctness needs it.
- `try_merge_map()` must avoid modifying maps with external users, because field updates are not atomic as a group.
