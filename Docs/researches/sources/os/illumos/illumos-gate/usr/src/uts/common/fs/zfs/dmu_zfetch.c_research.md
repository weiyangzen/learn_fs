# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_zfetch.c

## Purpose

Implements ZFS predictive prefetch stream tracking for dnodes. It detects sequential block access patterns, maintains per-dnode zfetch streams, issues speculative data and indirect-block prefetches, limits stream count and prefetch distance, and exports kstats for hit/miss and completion timing.

## Main Entry Points

- `zfetch_init()` / `zfetch_fini()`: create and destroy the `zfetchstats` kstat.
- `dmu_zfetch_init()` / `dmu_zfetch_fini()`: initialize and tear down a dnode's `zfetch_t`.
- `dmu_zfetch()`: predictive prefetch entry point called on block access.
- Internal helpers: `dmu_zfetch_stream_create()`, `dmu_zfetch_stream_remove()`, `dmu_zfetch_stream_orphan()`, `dmu_zfetch_stream_done()`.

## Control Flow And State

`dmu_zfetch()` exits immediately when predictive prefetch is disabled, indirect vdev mappings are not loaded, the access is the first block without the caller already holding the structure lock, or the file is too small to benefit. It then searches existing streams for an access that matches the expected next block, accepting either the exact next block or the previous prefetched block when alignment causes overlap.

A miss creates a new stream if the per-dnode stream limit allows it. Stream creation also reaps idle streams older than `zfetch_min_sec_reap`, unless they still have outstanding prefetch references. The effective max stream count is capped for small files so streams can plausibly be non-overlapping.

On a hit, the stream doubles its data prefetch distance up to `zfetch_max_distance` and separately doubles indirect prefetch distance up to `zfetch_max_idistance`. It updates stream block cursors under `zs_lock`, adds a reference count for expected async completions, drops zfetch locks, then issues `dbuf_prefetch_impl()` calls for level-0 data and level-1 indirect blocks. Completion callbacks update timing kstats and free orphaned streams once outstanding prefetches finish.

## Dependencies

Depends on dnode structure locks, dbuf prefetch, SPA indirect-vdev readiness, list/rwlock/mutex primitives, zfs_refcount for outstanding async prefetches, and kstat counters.

## Risks

The logic is concurrency-heavy despite being performance-oriented. Streams can outlive their parent zfetch structure, so orphaning and completion refcounts must stay balanced. The function intentionally drops locks before issuing prefetch I/O; stale stream state is handled by locked rechecks. Tunables directly affect wasted I/O versus sequential-read benefit.
