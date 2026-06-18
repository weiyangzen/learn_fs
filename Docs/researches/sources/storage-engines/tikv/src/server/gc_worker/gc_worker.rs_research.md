# sources/storage-engines/tikv/src/server/gc_worker/gc_worker.rs

## Purpose

This file implements the GC worker service and its task executor. It handles region GC, key-list GC from compaction filters, raw key GC, unsafe destroy range, orphan default-CF version cleanup, runtime config refresh, worker lifecycle, automatic GC startup, and automatic compaction startup.

## Important APIs, Types, And Functions

- `GcSafePointProvider` abstracts safe-point lookup; `Arc<PdClient>` implements it through `get_gc_safe_point`.
- `GcTask<E>` is the worker command enum: `Gc`, `GcKeys`, `RawGcKeys`, `UnsafeDestroyRange`, `OrphanVersions`, and test-only `Validate`.
- `GcRunnerCore<E>` owns store ID, engine, flow-info sender, write limiter, current config, config tracker, per-key-mode statistics, and coprocessor host.
- `GcRunner<E>` wraps `GcRunnerCore` and a YATP remote pool, spawning each scheduled task asynchronously after refreshing config.
- `get_regions_for_range_of_keys`, `get_keys_in_region`, and `init_snap_ctx` convert key batches into local regions and snapshot contexts.
- `GcRunnerCore::gc` runs range GC over a region after a table-property `need_gc` shortcut.
- `gc_keys` performs transactional MVCC GC for explicit keys, splitting work by region and flushing bounded `MvccTxn` batches.
- `raw_gc_keys` and `raw_gc_key` perform API v2 raw-key cleanup from explicit keys and safe point.
- `unsafe_destroy_range` bypasses Raft to delete a range directly, using fast file deletion plus key/blob cleanup for single RocksDB and per-region modifies for multi-RocksDB.
- `flush_deletes` handles vector fallback cleanup for orphan versions.
- `schedule_gc` and `sync_gc` are helper APIs for asynchronous and synchronous region GC.
- `GcWorker<E>` owns the lazy worker, scheduler, config manager, auto-GC handle, auto-compaction handle, feature gate, and region info provider.

## Control Flow

Scheduled tasks enter `GcRunner::run`, refresh config, clone runner core, and run on the future pool. `GcTask::Gc` checks MVCC properties before scanning region keys in `batch_keys` chunks and invokes `gc_keys`. `GcTask::GcKeys` and `RawGcKeys` operate on key vectors emitted by compaction filters, map them to local regions, and record handled versus wasted key metrics. `UnsafeDestroyRange` first emits flow notifications and coprocessor pre-delete hooks, then deletes files/ranges directly in local RocksDB or sends per-region delete-range modifies in multi-RocksDB mode. `OrphanVersions` acquires an ingest latch over the affected key span, then either writes the stored write batch synchronously or flushes individual deletes through the engine abstraction.

`GcWorker::start` starts the lazy worker with a `GcRunner`. `start_auto_gc` initializes the global compaction-filter context, creates `GcManager`, and starts its polling thread. `start_auto_compaction` initializes the MVCC read tracker and starts `CompactionRunner`. `Drop` stops manager, compaction runner, and worker only when the last cloned worker reference is released.

## State And Persistence Behavior

GC changes are persisted through `engine.modify_on_kv_engine`, raw/default-CF deletes, RocksDB range deletion APIs, and write batches. The write limiter is refreshed from online config and throttles GC write size. Statistics are accumulated per key mode and flushed to Prometheus counters after tasks. Unsafe destroy range also sends `FlowInfo` before/after events and hints range changes to the engine. The worker queue capacity is bounded by `GC_MAX_PENDING_TASKS`; unsafe destroy range uses `schedule_force` so it can still run when normal GC is full.

## Dependencies And Integration Points

This file integrates PD safe points, region metadata, raftstore coprocessor host, TiKV storage snapshots, MVCC reader/transaction GC logic, raw API v2 key/value encoding, RocksDB CF/range deletion APIs, flow-info signaling, failpoints, YATP pools, online config, compaction filter metrics, and auto-GC/auto-compaction components from sibling modules.

## Risks

- Unsafe destroy range bypasses Raft and relies on the caller guarantee that the range will not be accessed again.
- Region/key mapping assumes sorted key batches and local-peer filtering; gaps or stale region info can leave garbage.
- `keys.first().unwrap()` in key-GC paths requires non-empty key batches from callers.
- `OrphanVersions` for single RocksDB unwraps `kv_engine`; callers must only send write-batch orphan tasks where a local RocksDB exists.
- Multi-RocksDB unsafe destroy range has TODOs for flow info and region-size clearing parity.
- Config refresh happens per scheduled task, so long-running tasks keep the config snapshot they started with.

## Test Signals

Tests cover region selection for key GC, unsafe destroy range across boundary cases, compaction-filter key cleanup with region info, GC statistics, raw key GC, scan range limiting and large write-batch continuation, forced unsafe destroy range when the worker queue is full, key iteration across regions, multi-RocksDB GC/key/raw/destroy-range behavior, online thread-count scaling, and ingest-latch interaction for orphan-version cleanup.
