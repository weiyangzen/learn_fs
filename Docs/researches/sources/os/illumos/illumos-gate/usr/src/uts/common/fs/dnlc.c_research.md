# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dnlc.c

This file implements the illumos Directory Name Lookup Cache (DNLC) and a separate directory-entry cache. It caches name-to-vnode lookups, negative lookups, and directory entry/free-space metadata for filesystems that use the directory cache API.

Core responsibilities:
- Maintains the global DNLC hash table of `ncache_t` entries.
- Tracks vnode references held by DNLC separately through `v_count_dnlc`.
- Supports negative-cache hits through `negative_cache_vnode` / `DNLC_NO_VNODE`.
- Provides purge APIs by vnode, VFS, filesystem vnodeops, and whole-cache.
- Shrinks the cache asynchronously under pressure through `system_taskq`.
- Provides a second directory cache for name-to-handle and free-space-handle metadata.
- Exposes kstats through legacy `ncstats` and named `dnlcstats`.

Name-cache operations:
- `dnlc_init` sizes the cache, creates hash buckets and locks, initializes rotors, creates the directory-space kmem cache, initializes directory-cache global state, prepares the negative vnode, and installs kstats.
- `dnlc_enter` inserts a new `(directory vnode, name) -> vnode` mapping unless it already exists.
- `dnlc_update` inserts or updates a mapping, and removes stale negative entries if allocation fails.
- `dnlc_lookup` searches the hash bucket, moves deep hits toward the front, returns a caller-held vnode, and counts negative hits separately.
- `dnlc_remove` deletes one named entry.
- `dnlc_purge` purges all entries.
- `dnlc_purge_vp` removes entries referring to a vnode and stops once `v_count_dnlc` reaches zero.
- `dnlc_purge_vfsp` removes entries for a VFS, optionally bounded by count.
- `dnlc_fs_purge1` frees one candidate entry for a filesystem vnodeops table, preferring vnodes with no cached data and only DNLC reference.
- `dnlc_reduce_cache` schedules cache reduction.
- `dnlc_get` allocates variable-sized name-cache entries, enforces `dnlc_max_nentries`, and triggers reduction.
- `do_dnlc_reduce_cache` reclaims entries down to the low-water target or a requested percentage target.

Reference and deadlock model:
- `VN_HOLD_DNLC` increments `v_count_dnlc` and only takes a real vnode hold for the first DNLC reference.
- `VN_RELE_DNLC` releases via `vn_rele_dnlc`.
- Purge routines collect vnode releases into stack arrays and release after dropping hash locks to avoid inactive-path recursion and DNLC deadlocks.
- Hash buckets each have their own mutex; global scans process bounded batches and retry chains when necessary.

Directory-cache operations:
- `dnlc_dir_lookup` looks up names in partial or complete directory caches and can return `DFOUND`, `DNOENT`, or `DNOCACHE`.
- `dnlc_dir_start` creates a directory cache if enabled and within size thresholds.
- `dnlc_dir_add_entry` adds name-to-handle entries, dynamically resizing the name hash table and aborting/purging on memory pressure or excessive size.
- `dnlc_dir_add_space` adds free-space records, dynamically resizing the free-space hash table.
- `dnlc_dir_complete` marks a cache complete so misses can become definite `DNOENT`.
- `dnlc_dir_abort` frees all entries, free-space records, hash tables, and the directory-cache object.
- `dnlc_dir_purge` removes a directory cache from the global list and aborts it.
- `dnlc_dir_rem_entry`, `dnlc_dir_rem_space_by_len`, and `dnlc_dir_rem_space_by_handle` remove cached records and may purge undersized caches.
- `dnlc_dir_update` changes an entry handle in-place.
- `dnlc_dir_fini` tears down a directory cache anchor.
- `dnlc_dir_reclaim` is the kmem reclaim callback; it purges least-recently-used directory caches until enough entries have been freed.
- `dnlc_dir_adjust_nhash` and `dnlc_dir_adjust_fhash` resize directory-cache hash tables.

Tuning and observability:
- Name-cache sizing is controlled by `ncsize`, `nc_hashavelen`, `dnlc_low_water_divisor`, and related low/high-water values.
- Directory caching is controlled by `dnlc_dir_enable`, min/max size tunables, hash sizing shifts, and reclaim thresholds.
- Named kstats track hits, misses, negative hits, enter/double-enter counts, purge counts, eviction heuristics, and directory-cache outcomes.

Research notes:
- DNLC is central VFS infrastructure, not tied to devfs or sdev specifically.
- The separate directory cache is handle-oriented and supports both name lookup acceleration and directory free-space reuse.
- Memory-pressure behavior is intentionally conservative: cache creation/addition can return `DNOCACHE`, purge existing directory caches, or mark an anchor with `DC_RET_LOW_MEM`.
