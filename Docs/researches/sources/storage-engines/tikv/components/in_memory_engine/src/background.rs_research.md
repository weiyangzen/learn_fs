# sources/storage-engines/tikv/components/in_memory_engine/src/background.rs

## Purpose

Implements all asynchronous maintenance for the in-memory engine: loading cache regions from RocksDB snapshots, periodic GC/filtering, memory-pressure eviction, top-region load/evict decisions, delayed range deletion, lock-CF tombstone cleanup, optional cross-check startup, pending-region load triggering through raftstore, and PD region-label cache hints.

## Important APIs, Types, And Functions

`BackgroundTask` is the central worker command enum. Its variants cover `Gc(GcTask)`, `LoadRegion`, `MemoryCheckAndEvict`, `DeleteRegions`, `TopRegionsLoadEvict`, `CleanLockTombstone`, `TurnOnCrossCheck`, `SetRocksEngine`, and `CheckLoadPendingRegions`. `BgWorkManager` owns the primary worker, delete worker scheduler, ticker worker, engine core, and optional `RegionInfoProvider`; its `schedule_task` routes delete work to a separate scheduler and everything else to the main background runner. `PdRangeHintService` implements `RangeHintService` and watches PD region-label rules with label key `cache`, loading or evicting ranges when rules are added or removed.

`BackgroundRunner` is the main `Runnable`/`RunnableWithTimer`. It fans work out to dedicated workers/remotes: sequential region load, delete range, sequential GC, load/evict, lock cleanup, and optional cross-check worker. `BackgroundRunnerCore` contains shared engine/memory/statistics state and implements `regions_for_gc`, `gc_region`, snapshot-load completion/failure handling, and `top_regions_load_evict`. `DeleteRangeRunner` processes `DeleteRegions` and delays deletion while regions are being written or GCed. `Filter` is the GC compaction-filter analog for write/default CFs, with `split_ts` and `parse_write` validating MVCC key/value formats.

## Control Flow

`BgWorkManager::new` starts `BackgroundRunner` and `start_tick`. The ticker fires GC at `gc_run_interval`, load/evict at `load_evict_interval`, and pending-region checks about every five seconds. GC obtains a PD TSO, computes a safe point as current physical time minus the configured interval, schedules `BackgroundTask::Gc`, and the runner then asks RocksDB for the oldest live snapshot sequence number before spawning per-region filtering. The safe point used for each region is additionally capped by active in-memory snapshots and historical evicted-region snapshots.

Region loading is scheduled from `RegionCacheMemoryEngineCore::prepare_for_apply` after a pending region is marked `Loading` and a RocksDB snapshot is captured. `do_load_region` rejects canceled or stop-threshold loads, scans all `DATA_CFS` over the region range, inserts visible snapshot keys into skiplist CFs with the snapshot sequence number, accounts memory per entry, and aborts if capacity is reached. After loading, it fetches PD TSO and immediately runs `Filter` over the loaded region to remove old MVCC versions before marking the region `Active`; failures and cancellations mark regions evicting and enqueue delete-range work.

Memory pressure enters through `MemoryCheckAndEvict`, which delegates to `RegionStatsManager::evict_on_evict_threshold_reached` and clears the `memory_checking` flag when finished. Periodic `TopRegionsLoadEvict` collects hot regions and stale cached regions from `RegionStatsManager`, evicts selected cached regions, waits for eviction callbacks, then loads only as many new pending regions as the stop-load threshold can likely fit. `CheckLoadPendingRegions` sends raft casual messages to region leaders so a callback can call `prepare_for_apply` with a fresh disk snapshot.

## State And Persistence Behavior

The module does not create durable IME state. It mirrors RocksDB snapshot data into process-local skiplists and persists only indirectly by reading RocksDB snapshots and PD metadata. Region states and safe points live in `RegionManager`; `Loading`, `LoadingCanceled`, `Active`, `Evicting`, and historical snapshot metadata gate load completion, GC, and deletion. Memory is controlled through `MemoryController::acquire`/`release`; if an inserted `InternalBytes` later drops, it releases its recorded allocation. Metrics record memory usage, cache counts, safe points, GC filtering totals, and load/GC durations.

Deletes are deliberately asynchronous. `DeleteRangeRunner` removes all CF data for evicting regions only when region metadata shows no active write or GC. It then calls `RegionManager::on_delete_regions`, which is the point where region metadata and eviction callbacks can be finalized. GC deletion order is conservative: `Filter` caches MVCC delete keys and skiplist tombstones so older versions are removed before the delete marker that hides them.

## Dependencies And Integration Points

Depends on `engine_rocks` for `RocksEngine`/`RocksSnapshot`, `engine_traits` for CF names, region cache traits, snapshots, iterators, range hints, and eviction callbacks, `pd_client` for TSO and GC-safe-point access, `raftstore` for region info and casual load callbacks, `tikv_util::worker` for scheduling, `crossbeam` epoch/skiplist iteration safety, `txn_types` for MVCC keys and writes, and local modules `region_manager`, `region_stats`, `region_label`, `memory_controller`, `keys`, `write_batch`, `metrics`, and `cross_check`. Public integration is through `BgWorkManager`, `BackgroundRunner`, `BackgroundTask`, `GcTask`, and `PdRangeHintService`, mostly re-exported or called by `engine.rs`.

## Risks

The code is concurrency-sensitive: deletion must not race apply writes or GC, loading can be canceled while region epochs split, and GC must respect active snapshots plus historical evicted snapshots. Safe-point computation depends on PD TSO availability and wall-clock/physical timestamp assumptions. Memory accounting is approximate because skiplist node overhead is estimated, so thresholds can be crossed during load. Filter correctness is high-risk because deleting the wrong MVCC write/default pair can expose stale versions or remove visible values. `start_tick` updates `tso_timeout` from the old GC interval before assigning the new interval, which is worth reviewing if interval changes are important. PD label-watch handling currently has a TODO for richer eviction semantics when cache labels change.

## Test Signals

The in-file tests cover filter behavior, delete writes, region-scoped GC, GC after split, overwrite writes, snapshot-blocked GC, historical-region snapshot constraints, background load from RocksDB, GC-region selection, PD label hint loading and removal, load stop threshold, load capacity failure cleanup, online memory config changes, and PD TSO use for GC. Failpoints under `tests/failpoints/test_memory_engine.rs` exercise cancellation, write-batch interactions, and background timing. Metrics and logs are also key operational signals for memory pressure, safe-point drift, and load/evict decisions.
