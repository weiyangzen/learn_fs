# sources/storage-engines/tikv/components/in_memory_engine/src/write_batch.rs

## Purpose
`write_batch.rs` implements `RegionCacheWriteBatch`, the in-memory-engine write batch used to mirror Raft apply writes into the region cache skiplist. It is the bridge between `engine_traits::Mutable`/`WriteBatch` operations and `RegionCacheMemoryEngine` internals: region preparation, memory admission, write buffering, skiplist insertion with encoded sequence numbers, and eviction when the cache cannot safely accept writes.

## Important APIs, Types, and Functions
- `RegionCacheWriteBatch` tracks `region_cache_status`, buffered entries, savepoints, sequence number, current/prepared/written regions, and accumulated prepare time.
- `prepare_for_region` must be called before writes for each peer delegate. It validates the same region is not prepared non-contiguously, records the previous written region, asks `engine.prepare_for_apply`, and updates `current_region`.
- `set_sequence_number` is one-shot and feeds `write_impl`; `write_opt` errors if no sequence number was set.
- `process_cf_operation` gates puts/deletes by region cache state, engine enablement, and memory quota, evicting on disabled or capacity-reached conditions.
- `RegionCacheWriteBatchEntry` stores cf id, user key, and either `PutValue(Bytes)` or deletion. `write_to_memory` encodes internal keys with `encode_key(key, seq, ValueType)` and inserts into the skiplist CF handle.
- `maybe_compact_lock_cf` schedules `BackgroundTask::CleanLockTombstone` when lock CF modification bytes exceed the 16 MiB threshold.

## Control Flow
Normal flow is `prepare_for_region` -> `put_cf`/`delete_cf`/`delete_range_cf` -> `set_sequence_number` -> `write`. Each mutation either appends an entry to `buffer` or evicts the current region and stops buffering for it. `write_impl` records the last region, drains `buffer`, counts operations per CF, writes entries with monotonically increasing RocksDB sequence numbers, clears in-being-written flags, updates lock modification bytes, and records histograms. Savepoints only track buffer length; rollback truncates buffered entries.

## State and Persistence Behavior
Data is not persisted by this file; it is written to the memory engine's skiplist and must stay consistent with the disk engine sequence number supplied by RocksDB apply. Memory is pre-acquired based on encoded key/value size, then real skiplist/node overhead is charged through `InternalBytes` and memory-controller ownership. Regions can remain in manager state while loading or active; eviction removes their cached range asynchronously. `clear` is important because an empty batch that was prepared but never written still needs to clear region in-written flags.

## Dependencies and Integration Points
The file depends on `engine_traits` write traits and CF names, `kvproto::metapb::Region`, crossbeam epoch guards, the memory controller, region manager, background worker, metrics, and TiKV failpoints. It integrates with RocksDB sequence numbering, in-memory-engine snapshot visibility, lock tombstone cleanup, and batch-system apply ordering assumptions.

## Risks
The code relies on the invariant that a region is not prepared, interrupted by another region, then prepared again in the same batch-system round; violation panics. Memory accounting intentionally excludes skiplist node overhead during admission, so real usage can exceed capacity after flush. Missing `clear_written_regions` would block range deletion/eviction. Delete range evicts whole regions rather than deleting keys, so callers must understand the coarser behavior. `should_write_to_engine` is unimplemented because this batch is not a normal disk batch.

## Test Signals
Inline tests cover skiplist writes, savepoints, write-clear-delete cycles, pending-region prepare behavior, memory-controller eviction, config disable/enable behavior, outdated pending region replacement, and dirty data during prepare. Failpoint tests in this subset add race coverage for eviction, loading, GC, and delete-range ordering.
