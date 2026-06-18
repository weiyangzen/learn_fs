# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_lru.c

## Purpose
`mdcache_lru.c` implements MDCACHE memory management: constant-time multi-lane LRU queues for entries and directory chunks, entry/chunk reference accounting, background demotion/release workers, export-aware cleanup, FD-cache integration, and dirmap eviction for whence-is-name readdir support.

## Important APIs, Types, and Functions
- `struct lru_q` and `struct lru_q_lane` implement per-lane L1, L2, cleanup, and active queues.
- `mdcache_lru_pkginit()` initializes LRU state, queues, fridge worker threads, and FD LRU parameters; `mdcache_lru_pkgshutdown()` stops workers and destroys queues.
- `mdcache_lru_get()` returns a newly allocated or recycled cache entry with sentinel and active references; `mdcache_lru_insert_active()` places a constructed entry on the active queue.
- `_mdcache_lru_ref()` and `_mdcache_lru_unref()` are the public ref/unref backends, handling active references, promotion, sentinel release, cleanup, final free, and pool accounting.
- `mdcache_lru_release_entries()` reaps reachable-but-idle entries while above high water.
- `mdcache_get_chunk()`, `_mdcache_lru_ref_chunk()`, `_mdcache_lru_unref_chunk()`, `lru_bump_chunk()`, and chunk reaping functions manage directory chunk cache memory.
- `mdc_lru_map_dirent()`, `mdc_lru_unmap_dirent()`, `dirmap_lru_init()`, and `dirmap_lru_stop()` maintain bounded cookie-to-name restart maps per export.

## Control Flow
Entries move among active, L1, L2, cleanup, and none states. Active references move entries to the active queue. When the final active reference is dropped, `make_inactive_lru()` returns the entry to L1 or L2 depending on whether it has ever been promoted. Background `lru_run()` demotes idle L1 entries to L2 and optionally releases entries above the high-water mark. Reaping uses the cache hash latch plus queue lane lock to ensure only sentinel-referenced, reachable entries are removed from the hash and recycled.

Cleanup is split from reachability. Killed entries are removed from the hash and pushed to cleanup; unref performs state wipe once, then final cleanup frees lower-FSAL resources, attributes, export mappings, keys, locks, and the pool object when refcount reaches zero.

Chunks follow a separate lane array. `chunk_lru_run()` demotes chunks and releases a target number based on chunk pressure and entry pressure. Chunk reaping must acquire the parent directory `content_lock` or skip the chunk to preserve lock order.

## State and Persistence Behavior
LRU state is process-local memory: `entries_used`, `entries_hiwat`, `entries_release_size`, `chunks_hiwat`, `chunks_lowat`, `chunks_used`, and `per_lane_work`. Entries and chunks are recycled when possible, not persisted. Dirmap entries are transient per-export cookie/name mappings with an LRU list, a high-water cap, and age-based cleanup.

## Dependencies and Integration Points
This file integrates with `mdcache_hash` for latch-protected hash removal, `mdcache_helpers` for entry and chunk cleaning, `fsal_close()` and lower-FSAL `release()` for object teardown, pool allocation for cache entries, fridgethr background workers, FD LRU helpers, export lookup via `get_gsh_export()`, and NFS initialization wait. LTTng tracepoints are emitted around ref/reap operations when enabled.

## Risks and Edge Cases
Major risks are refcount imbalance, freeing while state or export mappings still exist, lock inversion between hash partitions, LRU lanes, and directory content locks, cleanup queue double-processing, and export context mismatch during lower-FSAL release. Chunk reaping is risky because it may observe a parent entry being destroyed and must rely on lane locks plus successful content-lock acquisition. Dirmap returns names through a `fsal_cookie_t *` cast, so callers must free and interpret it carefully.

## Test Signals
Useful tests include concurrent lookup/ref/unref under high cache pressure, unexport with entries still referenced by protocol operations, repeated kill/unref cleanup, large directory chunk pressure, FD limit pressure, package shutdown while workers are running, dirmap eviction and expiry, and sanitizer runs for use-after-free or double-free in chunk/entry recycling.
