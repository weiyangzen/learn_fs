<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cache.h -->
# sources/storage-engines/wiredtiger/src/include/cache.h

## Purpose
Defines WiredTiger's core cache data structures, cache-operation enum, cache eviction controls, disaggregated shared disk image cache, and cache pool metadata. It is the shared state model consumed by inline accounting helpers, eviction, reconciliation, cache pool management, history-store logic, and disaggregated storage code.

## Important APIs, Types, and Functions
`WT_CACHE_OP` enumerates sync/cache operation modes: checkpoint, close, discard, and write-leaves.

`WT_CACHE_EVICTION_CONTROLS` stores application eviction tuning, including tolerance, minimum fill ratio, and atomic flags `WT_CACHE_EVICT_INCREMENTAL_APP`, `WT_CACHE_PREFER_SCRUB_EVICTION`, and `WT_CACHE_SKIP_UPDATE_OBSOLETE_CHECK`.

`WT_SHARED_DSK_ITEM` represents one shared disk image entry with hash linkage, data pointer/size, reference count, block metadata, file ID, and variable-length address cookie.

`WT_SHARED_DSK_CACHE_DEFAULT_HASH_SIZE` computes a best-effort bucket count from cache size. `WT_DSK_CACHE_STATE` and macros `WT_DSK_CACHE_CAN_READ`/`WT_DSK_CACHE_CAN_WRITE` gate disaggregated shared disk cache access.

`WT_SHARED_DSK_CACHE` stores the state byte, read-only transition time, hash table, lock array, sizing, and diagnostic maxima.

`WT_CACHE` is the central per-connection cache accounting structure. It tracks bytes and pages for dirty internal/leaf content, images, in-memory data, internal pages, reads/writes, updates, history-store usage, ingest/stable disaggregated buckets, cache pool state, and shared disk cache state.

`WT_CACHE_POOL` represents a shared cache across connections with lock/condition variable, size/chunk/quota/current usage, references, connection queue, manager flag, and active flag.

## Control Flow
This header is declarative. Runtime control flow lives in users of these fields: cache accounting increments/decrements counters, eviction reads thresholds and flags, shared disk cache operations check state before hash-table access, and cache pool management updates quotas and connection queues under `cache_pool_lock`.

## State and Persistence Behavior
All fields are in-memory state for a WiredTiger process. They influence persistence indirectly by controlling eviction, checkpoint write pressure, history-store cache pressure, and disaggregated shared disk image reuse. Shared disk cache entries hold disk-image bytes and block metadata in memory only; reference counts decide hash-table lifetime.

## Dependencies and Integration Points
The structures depend on WiredTiger queue macros, spin locks, condition variables, thread IDs, page block metadata, B-tree flags, file IDs, and connection cache size. Integration points include eviction server/app eviction, cache pool manager, history store, reconciliation, block/image accounting, disaggregated standby/leader step-up behavior, and per-btree cache accounting from `btree_inline.h`.

## Risks and Edge Cases
Most counters are approximate under concurrency but must not become nonsensical. Disaggregated cache state transitions are sensitive: active standby permits reads and writes, stepped-up leader is read-only, drained leader is dead. Shared disk cache reference counts require lock protection; misuse can leak image entries or free still-shared data. Ingest/stable counter buckets must stay aligned with B-tree flags or cache pressure calculations become misleading.

## Test Signals
Useful signals include cache eviction threshold tests, cache pool quota tests, history-store pressure tests, disaggregated shared disk cache read/write/step-up tests, diagnostic reference-count checks, and workload tests that compare cache statistics against expected page/image/update movements.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cache.h -->
