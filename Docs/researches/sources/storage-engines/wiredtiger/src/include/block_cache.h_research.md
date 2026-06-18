# sources/storage-engines/wiredtiger/src/include/block_cache.h

## Purpose
This header defines metadata for WiredTiger's optional block cache, which caches disk-identical blocks in a faster medium such as DRAM or NVRAM. It provides the item layout, global cache configuration, hash table state, eviction tuning, and metrics for deciding whether the cache is useful.

## Important APIs, Types, And Functions
`WT_BLKCACHE_DELTA` stores one delta payload associated with a cached block. `WT_BLKCACHE_ITEM` is a hash-bucket entry containing data bytes, optional deltas, reference counts, a frequency/recency counter, returned `WT_PAGE_BLOCK_META`, file id, address-cookie size, and flexible address bytes. `WT_BLKCACHE` owns hash buckets and locks, the eviction thread id, exit flag, aggressive eviction timeout, write/checkpoint population flags, optional memkind NVRAM handle, target sizes, filesystem-cache bypass heuristics, cache type, bytes used/max bytes, reference thresholds, and counters/histograms.

## Control Flow
The file itself has no functions, but its fields define runtime flow for block-cache lookup, insertion, eviction, and bypass. Lookups hash by file id plus address. Cache references increment `num_references` and `freq_rec_counter`; the eviction thread decrements counters and removes low-value blocks. The cache can skip population when filesystem cache is expected to be sufficient or overhead is too high.

## State And Persistence Behavior
The block cache is an in-memory or NVRAM-backed performance layer for blocks identical to on-disk content. It does not define database correctness state: cache misses should fall back to the block manager. `bytes_used`, reference counters, histograms, and overhead metrics are runtime-only. Optional NVRAM configuration points at a filesystem path and memkind allocation kind, but cached entries mirror persistent blocks rather than replacing them.

## Dependencies And Integration Points
The header integrates with block-manager read/write paths, page block metadata, eviction threads, connection configuration, statistics, and optional `ENABLE_MEMKIND`. It interacts with disaggregated/page-delta support through per-item deltas and block metadata.

## Risks
Concurrency risks center on per-bucket locking, item `ref_count`, eviction while readers hold data, and heuristic counters updated without precise synchronization. Flexible-array address storage must match the supplied cookie size. The cache must never return stale data for a reused block address or mismatched file id. NVRAM support adds allocator/device lifecycle risk.

## Test Signals
Test cache hits/misses by address and file id, concurrent lookups/removals, eviction frequency thresholds, byte accounting, histograms, bypass heuristics, cache-on-write/checkpoint toggles, NVRAM allocation when enabled, delta-bearing entries, and fallback correctness after eviction.
