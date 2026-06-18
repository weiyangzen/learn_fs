# sources/storage-engines/tikv/components/raftstore-v2/src/worker/tablet.rs

## Purpose
This file implements the raftstore-v2 tablet background worker. It performs time-consuming or destructive tablet maintenance outside the main raftstore FSM path: trimming data outside a region range, staged and direct tablet destruction, imported SST cleanup, memtable flushes, range deletes, and snapshot GC. It also retries destroy operations that are blocked by open RocksDB locks.

## Important APIs, Types, and Functions
- `Task<EK>` is the worker command enum. Variants include `Trim`, `PrepareDestroy`, `Destroy`, `DirectDestroy`, `CleanupImportSst`, `Flush`, `DeleteRange`, and `SnapGc`.
- `Task` helper constructors build correctly shaped commands, including path-based destroy tasks for tablets that were never opened.
- `Display for Task` provides structured task logging with region ids, keys, priorities, flush thresholds, and snapshot keys.
- `Runner<EK>` owns the `TabletRegistry`, `SstImporter`, `TabletSnapManager`, logger, destroy queues, and two YATP future pools: `high_pri_pool` for urgent non-CPU waits and `low_pri_pool` for background work.
- `trim()` deletes data outside `[region.start, region.end)` with WAL disabled, then asynchronously compacts both outside ranges and validates `check_in_range`.
- `pause_background_work()` disables flush during shutdown for open tablets and asynchronously waits for background compactions to pause before returning the path.
- `prepare_destroy()`, `destroy()`, `direct_destroy()`, and `process_destroy_task()` implement staged path deletion, persisted-index gating, locked-path retry, and final factory destruction.
- `flush_tablet()` flushes `DATA_CFS`, optionally synchronously for leader-triggered callbacks and with a threshold to skip recent active memtables.
- `delete_range()` uses WAL-disabled `DeleteFiles` plus `DeleteByKey` for a CF range and reports whether anything was written.
- `RunnableWithTimer::on_timeout()` retries pending destroys every ten seconds.

## Control Flow
Task dispatch is a direct match in `Runnable::run`. Trim tasks issue fast file-range deletes, then compact and validate asynchronously before dropping the tablet and invoking the callback. Prepare-destroy pauses background work and queues `(path, wait_for_persisted, callback)` under the region id, deduplicating by path. Destroy tasks compare the persisted index against each queued wait point; eligible paths are destroyed immediately if unlocked or moved to `pending_destroy_tasks` for timer retry. Direct destroys skip the persisted-index queue and try the same destroy path immediately.

Flush tasks first resolve the latest tablet from the registry. Missing tablets log a warning and still invoke callbacks. Leader flushes with callbacks are run in a future pool with synchronous flush and callback after tablet drop. Followers flush directly and asynchronously at RocksDB level. Delete-range tasks panic on unexpected task shape and on RocksDB delete failures, reflecting that partial delete failure is considered fatal.

## State and Persistence Behavior
This file directly changes tablet RocksDB state. Trim and delete-range use WAL-disabled writes and file deletion strategies; correctness depends on raft apply trace and flushed-index persistence elsewhere. Flush persists memtables into SSTs. Destroy removes tablet directories only after registry locks are gone and, for staged destroys, after the persisted apply index reaches the requested wait point. Snapshot GC removes tablet snapshot files via `TabletSnapManager`. SST cleanup deletes importer files.

## Dependencies and Integration Points
Key dependencies include `engine_traits` tablet APIs, `TabletRegistry`, `TabletContext`, `DATA_CFS`, `DeleteStrategy`, `ManualCompactionOptions`, `WriteOptions`, `raftstore::store::{TabletSnapKey, TabletSnapManager}`, `sst_importer::SstImporter`, `keys` data key helpers, and TiKV YATP pools. Failpoint `tablet_trimmed_finished` lets tests synchronize trim completion. The worker is used by split, merge, life-cycle, apply, and snapshot paths.

## Risks and Edge Cases
- Destroy is intentionally best-effort when paths are locked; pending tasks can accumulate if registry references are leaked.
- `process_destroy_task()` treats missing paths as consumed, which is correct for idempotence but can hide unexpected external deletion.
- Trim validates range cleanup but logs and returns without callback if delete or compaction fails; callers must tolerate callback absence on failure.
- Delete-range currently does not delete Titan blobs and panics on engine errors.
- High-priority flush routing depends on low-priority running task count; starvation or pool saturation could delay leader callbacks.
- The code sets `avoid_flush_during_shutdown` before background-work pause to prevent destroy from being blocked by wasteful flushes.

## Test Signals
The in-file unit tests cover races between destroy and trim, destroy of locked tablets after registry removal, duplicate/missing destroy paths, and timer retry behavior. Failpoint and integration tests in this subset add coverage for split resume, merge replay, delete-range persistence, data recovery after restart, and tablet-index/flushed-index invariants.
