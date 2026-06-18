# sources/storage-engines/wiredtiger/src/cache/cache.c

## Purpose

Owns top-level WiredTiger cache lifecycle and statistics plumbing. It creates `WT_CACHE`, applies cache configuration, initializes disaggregated standby shared-disk cache state when needed, publishes cache statistics, and verifies cache shutdown invariants.

## Important APIs, Types, And Functions

`__wt_cache_config` handles initial configuration and reconfiguration for `cache_size`, `cache_overhead`, and shared-cache transitions. `__wt_cache_create` allocates `conn->cache`, delegates common config, conditionally initializes `cache->shared_dsk_cache`, and populates initial stats. `__wt_cache_stats_update` snapshots many cache counters into connection statistics, including bytes in use, dirty bytes, image bytes, internal/leaf bytes, history-store bytes, page counts, eviction controls, and reconciliation maxima. `__wt_cache_destroy` checks that cache memory and dirty state have drained, destroys shared disk cache if present, and frees `conn->cache`.

The file centers on `WT_CONNECTION_IMPL`, `WT_CACHE`, connection stats arrays, disaggregated role config, shared cache flags, and the shared disk cache APIs in `shared_dsk.c`.

## Control Flow

Configuration first detects whether `shared_cache.name` is set and whether the connection was previously in a cache pool. Reconfiguring away from a shared cache temporarily marks `WT_CONN_RECONFIGURING_CACHE_POOL` and destroys the pool membership. Reconfiguring into a shared cache clears `conn->cache_size` so the pool can manage it. Non-shared mode reads `cache_size`; both modes set `cache->overhead_pct`.

Creation allocates cache memory before configuration because subsequent paths expect `conn->cache`. For disaggregated page-log standby nodes, it reads the role from config and initializes the shared disk cache only when not leader, then marks the disk cache active. Stats update computes aggregate values from atomics, derives leaf bytes defensively from total minus internal bytes, writes stat fields, and then calls eviction stats update. Destruction checks page, image, byte, and dirty counters, logs errors if shutdown is not clean, destroys shared disk cache if allocated, and frees the cache.

## State And Persistence Behavior

This file manages in-memory cache state, not persistent data files. Its settings determine cache capacity and overhead accounting for all page residency and eviction. For disaggregated standby, it creates a cross-checkpoint disk-image cache that can retain page images read from storage while the process runs. Destruction is an integrity check that all cached and dirty pages have already been reconciled, evicted, or otherwise released before connection teardown.

## Dependencies And Integration Points

Integrates with config parsing, cache pool management (`__wt_cache_pool_destroy`), disaggregated configuration, shared disk cache init/destroy, stat macros, atomic cache accounting helpers, eviction stat update, and reconciliation timing fields on the connection. Shared cache creation itself lives in `cache_pool.c`; this file coordinates the cache-size side of entering/leaving that mode.

## Risks

Reconfiguration must keep shared-cache flags consistent even when errors occur; the error path clears `WT_CONN_RECONFIGURING_CACHE_POOL`. Stats are race-tolerant but can momentarily see inconsistent counters, so derived leaf values must avoid underflow. Disaggregated shared disk cache initialization depends on config before metadata/recovery is available, which the source notes as a temporary dependency workaround. Shutdown warnings indicate leaks or dirty state that can imply earlier eviction/checkpoint failures.

## Test Signals

Useful signals include configuration tests for `cache_size`, `cache_overhead`, and shared-cache transitions; disaggregated standby startup verifying `cache_shared_dsk_hash_size` and active state; stat tests checking non-underflow and expected counter publication; and teardown tests that close clean connections without cache leak messages. Stress tests should combine eviction, history store, ingest/stable accounting, and reconfigure paths.
