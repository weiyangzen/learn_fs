# sources/storage-engines/tikv/components/raftstore/src/store/worker/raftlog_gc.rs

## Purpose
This file implements the background worker that garbage-collects obsolete raft log entries from the raft engine. It batches region log-GC requests, syncs the KV engine before deletion to preserve the "applied data is durable before its raft log is removed" invariant, writes raft-engine GC batches, and invokes optional completion callbacks after the batch has been consumed.

## Important APIs, Types, and Functions
`Task` carries one GC range: `region_id`, `start_idx`, `end_idx`, a `flush` flag, and an optional one-shot callback. `Task::gc(region_id, start, end)` constructs a normal GC task; `flush()` forces the runner to flush after enqueueing the task; `when_done()` attaches a callback invoked after the flush path finishes writing the raft batch.

`Runner<EK, ER>` stores queued tasks, `Engines<EK, ER>`, and `compact_sync_interval`. `Runner::new()` wires those dependencies. `raft_log_gc()` consumes a raft log batch with `sync=false` and exposes failpoints around the write. `flush()` is the core implementation. The runner implements both `Runnable` and `RunnableWithTimer`.

Constants control batching and logging: `MAX_GC_REGION_BATCH` flushes after more than 512 queued tasks, and `MAX_REGION_NORMAL_GC_LOG_NUMBER` marks unusually large per-region ranges for warning logs. Metrics include KV sync duration, raft write duration, failed GC count, and seek-operation count for `start_idx == 0`.

## Control Flow
`Runnable::run()` marks the operation as foreground-write IO, saves whether the task requested `flush`, pushes it into `tasks`, and calls `flush()` if the task requested flushing or the queue exceeds the batch limit. `RunnableWithTimer::on_timeout()` also calls `flush()`, and `shutdown()` flushes remaining work.

`flush()` returns immediately when no tasks are queued. Otherwise it hits the `worker_gc_raft_log_flush` failpoint, synchronously calls `kv.sync()` and panics on sync failure, takes the task queue, allocates a raft log batch sized to the task count, and iterates tasks. Callbacks are saved separately. Empty ranges (`start_idx == end_idx`) are treated as flush-only barriers. Non-empty ranges call `engines.raft.gc(region_id, start_idx, end_idx, &mut batch)`, logging and counting failures per task. After the loop, `raft_log_gc(batch)` consumes the batch; callbacks run after that attempt.

## State and Persistence Behavior
The only local state is the in-memory pending task queue. Persistence behavior is the file's main concern: it syncs the KV engine before consuming the raft log batch so applied key/value data is durable before raft logs needed for recovery are discarded. Raft log deletion is persisted by the raft engine's `gc()` plus `consume()` path.

The task callback is not a durability callback for KV sync alone; it runs after the raft batch consume attempt returns, even if some individual GC calls failed or the final consume failed. Empty-range tasks can be used as a flush/callback barrier without deleting logs.

## Dependencies and Integration Points
The worker is generic over `KvEngine` and `RaftEngine` and receives both through `engine_traits::Engines`. It relies on `RaftEngine::log_batch()`, `RaftEngine::gc()`, and `RaftEngine::consume()`, plus `KvEngine::sync()`.

It integrates with TiKV's worker framework through `Runnable` and `RunnableWithTimer`, with IO classification through `file_system::WithIoType(IoType::ForegroundWrite)`, with failpoints for test/fault injection, and with raftstore metrics in `store::worker::metrics`.

Upstream callers are raftstore peers or compact-log scheduling paths that know the safe `[start_idx, end_idx)` range after apply/compact progress.

## Risks and Edge Cases
The correctness-critical risk is deleting raft logs before applied KV data is durable; this is why `kv.sync()` occurs before raft deletion and panics on failure. Any future async/batched change must preserve that ordering.

Callbacks always run after the flush attempt, not only after successful deletion. If callers interpret callbacks as success notifications, failed `gc()` or `consume()` paths could cause incorrect assumptions. The code records metrics and logs but does not retry failed tasks after taking them from the queue.

Large GC ranges are allowed but warned about. `start_idx == 0` increments a seek metric because it likely forces range scanning from the beginning. Flush-only tasks use `start_idx == end_idx`, which means callers must not expect an empty range to validate region state.

## Test Signals
The in-file `test_gc_raft_log` creates test KV/raft engines, writes raft entries `0..100`, then verifies successive GC ranges remove exactly `[0,10)`, `[0,50)`, ignore an empty `[50,50)` range, and remove `[50,60)` while preserving later entries.

Additional useful tests would cover forced flush callbacks, timer/shutdown flush, injected raft consume failure, injected per-task `gc()` failure, and verifying callback semantics under failure.
