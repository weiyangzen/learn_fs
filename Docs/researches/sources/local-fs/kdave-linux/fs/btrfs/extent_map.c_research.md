# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent_map.c

This file implements the Btrfs per-inode extent-map cache. Extent maps describe file logical ranges as holes, inline data, prealloc ranges, compressed extents, or regular on-disk extents, and are stored in an rb-tree with reference counting and a modified-extents list for fast fsync.

Major responsibilities:
- Initializes/destroys the extent-map slab cache and per-inode `extent_map_tree`.
- Allocates, frees, inserts, looks up, searches, removes, and replaces extent maps under the tree rwlock.
- Validates extent-map alignment and on-disk length/offset invariants in debug builds.
- Merges adjacent compatible extent maps to reduce memory usage, while excluding pinned, compressed, logging, and modified extents.
- Handles insertion races from `btrfs_get_extent()` by returning an existing map or trimming/merging the new map into the uncovered range.
- Drops or replaces extent-map ranges, splitting maps around the removed range when possible and setting full-fsync state when modified extents cannot be preserved precisely.
- Splits pinned ordered extent maps when ordered extents are split.
- Implements the asynchronous extent-map shrinker worker that scans filesystem roots and inodes to reclaim evictable extent maps under memory pressure.

Key data flows:
- `btrfs_add_extent_mapping()` inserts a newly loaded map; on `-EEXIST`, it searches for the overlapping/nearby map and either returns that map or trims the new one to a gap between neighbors.
- `btrfs_unpin_extent_cache()` clears `EXTENT_FLAG_PINNED` after writeback has persisted a file extent item, updates generation, and attempts merge.
- `btrfs_drop_extent_map_range()` removes all maps intersecting a range, optionally skipping pinned maps and preserving outside portions with up to two split maps.
- `btrfs_replace_extent_map_range()` repeatedly drops overlapping maps and inserts a replacement until no insertion race remains.
- `btrfs_free_extent_maps()` coalesces shrinker requests through an atomic scan count and queues `em_shrinker_work`; the worker resumes from remembered root/inode positions.

Concurrency and lifetime:
- The rb-tree and modified list are protected by `extent_map_tree::lock`.
- Tree membership owns one reference; lookups and callers take/drop additional references with `btrfs_free_extent_map()`.
- Modified extents in `em->list` interact with fast fsync; removing recent modified maps forces full fsync to avoid missing unwritten file extent items.
- The shrinker uses trylocks on inode extent trees and `i_mmap_lock` to avoid racing fsync logging decisions while holding the extent-tree write lock.

Important invariants:
- Extent maps in a tree must not overlap.
- Regular extent-map fields are sectorsize aligned; holes and inline extents use sentinel disk addresses and zero offsets.
- Compressed extent maps are not merged because their physical and logical sizes differ and compression type matters.
- Pinned maps are protected from removal/merge unless callers explicitly clear the pinned state.
- The evictable extent-map counter is maintained only for non-testing filesystem tree roots.
