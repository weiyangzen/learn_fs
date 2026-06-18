# sources/storage-engines/tikv/src/storage/txn/txn_status_cache.rs

## Purpose
`txn_status_cache.rs` implements TiKV's in-memory cache of recent transaction states keyed by `start_ts`. It exists primarily to make late, stale prewrite retries safer: if a transaction is already known committed, the storage path can avoid an optimization that skips WRITE CF constraint checks for non-unique index keys. The file also contains the newer dual-cache design for ongoing large transactions, where `min_commit_ts` must remain visible while locks are still being resolved.

## Important APIs, Types, and Functions
`TxnState` models `Ongoing { min_commit_ts }`, `Committed { commit_ts }`, and `RolledBack`; `from_ts` converts raw timestamps and rollback state into this enum. `CacheEntry` pairs state with insertion/update time. `TxnStatusCacheEvictPolicy` is an `lru::EvictPolicy` that evicts entries only after a required keep duration or capacity pressure. `TxnStatusCache` owns sharded `normal_cache` and `large_txn_cache` vectors of padded mutex-protected LRU caches. Its public surface includes `new`, `new_for_test`, `with_slots_and_time_limit`, `upsert`, `insert_committed`, `get`, `get_committed_no_promote`, `get_committed`, and `remove_large_txn`.

## Control Flow
Construction divides total capacity across slots and builds two cache sets with separate retention durations. `upsert` routes ongoing entries with `min_commit_ts > start_ts` into the large-transaction cache; committed, rolled-back, and normal ongoing states use the normal cache and also update any existing large-cache entry. Retrieval checks the large cache first because it can hold a newer view of a transaction that also exists in normal cache. Normal committed-only reads intentionally skip large-cache lookup and can avoid LRU promotion.

## State and Persistence Behavior
All cache state is process-local memory; it is not persisted and is not replicated across TiKV nodes. Each entry records wall-clock milliseconds for eviction. Metrics update used and allocated cache size under the assumption that one cache instance exists per process. The cache can be disabled by zero capacity, making operations no-ops.

## Dependencies and Integration Points
The module depends on TiKV's custom `lru` implementation, `parking_lot::Mutex`, `crossbeam::CachePadded`, `txn_types::TimeStamp`, failpoints, and storage scheduler metrics. It integrates with transaction prewrite/commit/rollback paths that can upsert or query status, and with resolved-ts/large-transaction handling through the large cache.

## Risks and Test Signals
Risk centers on incomplete cluster-wide visibility, wall-clock changes, capacity eviction before stale requests arrive, and lock ordering between large and normal cache locks. The code documents the unsolved leader-transfer gap. Tests cover insertion, time and capacity eviction, disabled cache behavior, normal/large transitions, immutability of decided states, large-txn removal, and failpoint-driven lock-order deadlock resistance. Benchmarks cover insert/get and manual concurrent contention behavior.
