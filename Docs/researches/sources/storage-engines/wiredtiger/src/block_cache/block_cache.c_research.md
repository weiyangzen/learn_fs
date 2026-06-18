# sources/storage-engines/wiredtiger/src/block_cache/block_cache.c

## Purpose

`block_cache.c` implements the optional WiredTiger block cache and the block-manager open/setup entry point. It provides DRAM/NVRAM allocation, hash-bucket lookup/insert/remove, reference-safe eviction, cache bypass heuristics, cache destruction, configuration parsing, and `WT_BM` creation for file, tiered, or disaggregated objects.

## Important APIs, Types, and Functions

Important routines are `__wti_blkcache_get`, `__wti_blkcache_put`, `__wt_blkcache_remove`, `__wt_blkcache_destroy`, `__wt_blkcache_open`, and `__wt_blkcache_setup`. Private helpers include `__blkcache_alloc`, `__blkcache_free`, `__blkcache_should_evict`, `__blkcache_eviction_thread`, `__blkcache_estimate_filesize`, `__blkcache_init`, and `__blkcache_reconfig`. Core types are `WT_BLKCACHE`, `WT_BLKCACHE_ITEM`, `WT_BLKCACHE_DELTA`, `WT_BM`, and per-bucket spin locks.

## Control Flow

Lookup checks NVRAM bypass heuristics, hashes by address cookie plus btree file ID, locks the bucket, increments reference and frequency counters on hit, and tells callers whether subsequent put should be skipped. Put checks capacity and NVRAM overhead, copies page data and optional deltas outside the bucket lock, detects duplicate read inserts, inserts at the bucket head, and updates byte/block stats. Remove unlinks by address, waits for active references to drain, frees base/delta/meta buffers, and updates histograms/stats.

The eviction thread wakes once per second, scans buckets, decrements frequency/recency counters, avoids referenced blocks, avoids NVRAM eviction during high churn, and evicts least-reused stale blocks once the cache is above `full_target`.

`__wt_blkcache_open` delegates disaggregated URIs to the disaggregated manager, opens file URIs through `__wt_block_open`, or initializes a tiered multi-handle `WT_BM` with a handle array. `__wt_blkcache_setup` parses block-cache config, but currently logs a warning and returns without enabling when `block_cache.enabled` is true.

## State and Persistence Behavior

The cache is process-local and non-durable. It stores copied block images, optional delta arrays, page block metadata, file IDs, address bytes, reference counts, frequency counters, and global byte counters. NVRAM mode allocates from a memkind persistent-memory arena, but the cache contents are still managed as runtime cache state and destroyed on shutdown.

## Dependencies and Integration Points

This file is used by `block_io.c` read/write wrappers, `block_mgr.c` free paths, connection initialization/reconfiguration, tiered-object open, disaggregated object ownership, statistics, verbose logging, memkind when enabled, and the connection block-handle hash for file-size estimates.

## Risks and Edge Cases

The cache is currently disabled by setup even when configured, so code may be less exercised. Duplicate insert handling assumes write collisions are impossible outside diagnostics. Removal busy-waits until `ref_count` drains. Some counters intentionally race for speed. NVRAM bypass depends on approximate file-size and overhead estimates. Reconfiguration only accepts identical settings and rejects meaningful changes.

## Test Signals

Test signals include cache hit/miss stats, duplicate read insert path, removal waiting for references, eviction above `full_target`, NVRAM unsupported builds returning configuration errors, setup's disabled warning, destroy-time nonzero ref-count errors, and reference histograms printed on destroy.
