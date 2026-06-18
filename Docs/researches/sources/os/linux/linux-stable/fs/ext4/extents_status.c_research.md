# File Research: sources/os/linux/linux-stable/fs/ext4/extents_status.c

This file implements ext4's in-memory extent status tree and the auxiliary pending cluster reservation tree. The extent status tree caches logical ranges as written, unwritten, delayed, or hole extents; it supports map lookups, FIEMAP/SEEK behavior, delayed allocation accounting, shrinker reclaim, and bigalloc reservation correctness.

Major responsibilities:
- Extent status tree lifecycle: slab creation/destruction, per-inode tree initialization, object allocation/free, per-superblock shrinker registration, and inode participation in the shrink list.
- Lookup and scanning: `ext4_es_lookup_extent()`, `ext4_es_find_extent_range()`, `ext4_es_scan_range()`, and `ext4_es_scan_clu()` search by logical block/range/cluster, using a cached recent extent before RB-tree search.
- Insert/cache/remove: `ext4_es_insert_extent()` modifies authoritative status ranges, `ext4_es_cache_extent()` only caches compatible on-disk information, and `ext4_es_remove_extent()` removes ranges while splitting edge extents when needed.
- Merging and accounting: adjacent extents with compatible status and contiguity are merged; counters track all ES objects and shrinkable ES objects.
- Reservation accounting: removal paths count delayed blocks/clusters and release delayed allocation reservations through `ext4_da_release_space()` or `ext4_da_update_reserve_space()`.
- Shrinker support: written/unwritten/hole extents are reclaimable; delayed extents are kept because FIEMAP, SEEK_DATA/SEEK_HOLE, and bigalloc accounting rely on them.
- Pending reservations: bigalloc filesystems maintain an RB-tree of logical clusters with pending reservations. Helpers insert, remove, query, and revise these entries as delayed/unwritten/written extents change.
- Debug/test support: optional aggressive consistency checks compare ES state against the on-disk extent tree or indirect block mapping.

Important design points:
- Each inode owns an `ext4_es_tree` protected by `EXT4_I(inode)->i_es_lock`.
- The tree is ordered by logical block and stores physical block plus status flags in `extent_status.es_pblk`.
- `tree->cache_es` is a single recently used extent pointer used as a fast path for common lookup and range scans.
- `ext4_es_must_keep()` currently preserves delayed extents from shrinker reclaim.
- Insertion first removes overlapping status entries, then inserts the replacement and merges with neighbors. Memory allocation failures are retried using nofail preallocation for must-keep or required operations.
- `ext4_es_cache_extent()` is intentionally weaker than `ext4_es_insert_extent()`: it refuses to overwrite conflicting existing state, except that cached holes may coexist with delayed state.
- Fast-commit replay mode bypasses most ES operations because replay rebuilds or adjusts mappings outside the normal steady-state cache rules.
- Pending reservation logic is specific to bigalloc plus delayed allocation. It avoids reading disk extents during page invalidation and protects reserved-cluster accounting when clusters mix delayed/unwritten and allocated states.

Key invariants:
- Only one of written, unwritten, delayed, or hole status types may be set at a time; referenced is an additional reclaim hint.
- RB-tree extents must not overlap and are merged when status and logical/physical adjacency allow it.
- Delayed extents are non-reclaimable.
- Shrinker-visible counters and per-superblock counters are updated whenever extents become reclaimable/non-reclaimable or are freed.
- `i_es_seq` is incremented on successful authoritative tree modifications so lookup users can detect ES changes.
- Pending reservation entries are keyed by logical cluster and are manipulated under `i_es_lock`.
- Removal accounting must not release reservations for clusters that still contain delayed blocks outside the removed range or that have pending reservations representing allocated-but-delayed-shared clusters.

External interfaces include ES initialization/teardown, insert/cache/remove/find/lookup/scan, shrinker registration and proc reporting, pending tree initialization, pending reservation insert/remove/query paths, delayed extent insertion, and clearing discretionary ES cache entries.
