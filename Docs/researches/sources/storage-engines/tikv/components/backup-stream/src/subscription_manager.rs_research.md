# sources/storage-engines/tikv/components/backup-stream/src/subscription_manager.rs

## Purpose
`subscription_manager.rs` serializes region subscription operations for backup-stream observation. It starts and stops region observation, retrieves the last safe checkpoint for a region, launches initial scans from that checkpoint, retries transient failures with backoff, reacts to region changes and memory pressure, and periodically resolves per-region checkpoints into a store-level `ResolvedRegions` result used by flushing.

The manager is the bridge between raftstore leadership/region events, metadata checkpoints, initial snapshot scanning, incremental event observation, and router task ranges. Its correctness determines whether backup-stream observes the right leader regions from the right timestamp without advancing checkpoints past unfinished initial scans or unresolved locks.

## Important APIs, Types, And Functions
`ResolvedRegions` packages `Vec<ResolveResult>` plus the computed global checkpoint. `new()`, `take_resolve_result()`, `resolve_results()`, and `global_checkpoint()` are consumed by router flush code and checkpoint management.

`InitialScan` is a private async trait abstracting initial scan execution. Its production implementation for `InitialDataLoader<E, RT>` obtains an observe snapshot with `observe_over_with_retry()`, installs a PITR `ChangeObserver`, and scans initial data from the provided start timestamp. `ScanCmd` holds a region, observe handle, last checkpoint, feedback channel, and wait-group work token. `ScanCmd::exec_by()` runs the scan and records CF statistics.

`scan_executor_loop()`, `spawn_executors()`, `spawn_executors_to()`, `create_scan_pool()`, and `ScanPoolHandle::request()` implement the dedicated initial-scan runtime. The pool uses TiKV's log-backup scan thread name and sets filesystem IO type to replication. Queue and executing lengths update `PENDING_INITIAL_SCAN_LEN`.

`RegionSubscriptionManager<S, R>` owns region info provider, metadata client, range router, endpoint scheduler, `SubscriptionTracer`, failure counts, memory quota, weak self-messenger, scan pool handle, wait group for scans, and `advance_ts_interval`. `RegionSubscriptionManager::start()` constructs the mpsc channel and returns `(Sender<ObserveOp>, future)` for the operator loop.

The operator methods are `region_operator_loop()`, `start_observe()`, `try_start_observe()`, `observe_over_with_initial_data_from_checkpoint()`, `spawn_scan()`, `on_observe_result()`, `retry_observe()`, `is_available()`, `refresh_resolver()`, `on_high_memory_usage()`, `schedule_start_observe()`, `get_last_checkpoint_of()`, `find_task_by_region()`, `issue_fatal_of()`, and `wait()`. `should_retry()` classifies errors that should not be retried, such as epoch mismatch, not leader, stale observe id, region not found, observe canceled, and raftstore not-leader/epoch errors. `backoff_for_start_observe()` provides capped exponential retry delay with a failpoint override.

## Control Flow
`RegionSubscriptionManager::start()` creates a bounded mpsc channel, spawns scan executors, copies the sink router and scheduler from the initial loader, and returns `region_operator_loop()`. All `ObserveOp` messages are handled sequentially in that loop, preserving start/stop/refresh ordering for the shared `SubscriptionTracer`.

On `ObserveOp::Start`, `start_observe()` first calls `is_available()` to ensure the region still exists, this store is leader, the supplied epoch is not stale, and any existing running subscription for the same handle can be removed. It then marks the region pending and calls `try_start_observe()`. `try_start_observe()` finds the task by region range, retrieves the last region checkpoint from metadata, and calls `observe_over_with_initial_data_from_checkpoint()`. That method registers the region as running with a `TwoPhaseResolver` stable timestamp equal to the checkpoint, upgrades the weak self-messenger, and enqueues a `ScanCmd` to the scan pool.

The scan pool receives `ScanCmd`, spawns an async task per command, executes the initial scan, then sends `ObserveOp::NotifyStartObserveResult` back to the manager with the region, observe handle, and optional boxed error. On success, `on_observe_result()` clears failure count and calls `phase_one_done()` on the matching subscription resolver. On failure, it moves the matching running subscription back to pending, skips retry for unretryable errors, or calls `retry_observe()`. Retry increments per-region failure count, checks `is_available()` again, and schedules a delayed `ObserveOp::Start` using capped exponential backoff. Too many retries become a fatal endpoint task for the region range.

`ObserveOp::Stop` deregisters the region unconditionally. `Destroy` deregisters only if epoch comparison says the new destroy event covers the active subscription. `RefreshResolver` tries to update only region metadata if the epoch version is unchanged; otherwise it deregisters and, if the region still maps to a task, starts observation again from the latest checkpoint. If refresh fails to get checkpoint or enqueue scan, it synthesizes a `NotifyStartObserveResult` through the endpoint scheduler so normal retry handling applies.

`ObserveOp::ResolveRegions` waits up to five seconds for pending initial scans, asks `BackupStreamResolver` for leader/current regions with an optional `advance_ts_interval`, calls `SubscriptionTracer::resolve_with(min_ts, regions)`, chooses the minimum region checkpoint or `min_ts` when no regions are observed, updates metrics for the smallest checkpoint region, logs non-trivial blockers, and invokes the callback with `ResolvedRegions`.

`ObserveOp::HighMemUsageWarning` deregisters the inconsistent region, logs memory usage, and schedules a delayed restart with a base 60-second backoff plus jitter. This drops resolver lock memory for a problematic region and later rebuilds it by initial scan.

## State And Persistence Behavior
The manager's own state is process memory: subscription map, failure counts, queued scans, and retry timers. Durable input comes from `MetadataClient::get_region_checkpoint(task, region)`, which returns the timestamp from which initial scan should start. Durable output is indirect: resolved region checkpoints flow into router metadata/global checkpoint updates, and fatal errors flow into endpoint task handling.

The subscription state machine uses `Pending` as a placeholder while checkpoint lookup and initial scan are in progress. Running subscriptions contain an `ObserveHandle` and `TwoPhaseResolver`. During initial scan, the resolver's stable ts prevents checkpoint advancement beyond the scan start even while incremental events are being observed concurrently. Only after scan success does `phase_one_done()` replay buffered incremental lock/unlock events and allow normal resolved-ts progression.

The wait group in `scans` tracks in-flight initial scans. `ResolveRegions` waits briefly for it to drain, but if it times out it still resolves with current subscription state; phase-one subscriptions will report their stable timestamp rather than blocking indefinitely. Retry state is bounded by `TRY_START_OBSERVE_MAX_RETRY_TIME`; exceeding it emits a fatal endpoint task and clears failure count.

## Dependencies And Integration Points
This module depends on raftstore region information and observe handles, `InitialDataLoader`, `MetadataClient` and metadata stores, `Router` range lookup, endpoint `ObserveOp` and `Task`, `BackupStreamResolver`, `SubscriptionTracer`, `ResolveResult` and checkpoint types, TiKV memory quota, thread builder hooks, metrics, failpoints, and worker scheduler.

It integrates with leadership/region-change producers that send `ObserveOp::Start`, `Stop`, `Destroy`, and `RefreshResolver`; with initial scan code that writes historical data into the router; with incremental observer code that sends KV events and lock changes; and with checkpoint/flush code that asks for `ResolvedRegions`.

## Risks And Edge Cases
`find_task_by_region()` uses router `find_task_by_range()`, which returns only one overlapping task. If a region overlaps multiple backup task ranges, subscription may only be associated with one task. The router source itself flags this limitation.

Retry behavior must distinguish stale commands from recoverable failures. `is_available()` removes an existing subscription only when the handle id matches; otherwise it treats the retry as stale. Incorrect handle matching could stop a fresh observation or revive an old one. Unretryable errors leave the region pending until a later stop/refresh cleans it up, which is intentional but can be confusing in metrics.

`ResolveRegions` forces progress after a five-second scan wait. The two-phase resolver makes this safe for phase-one regions, but if a subscription is absent or incorrectly marked running without a stable ts, checkpoints could advance too far. `wait()` returns `true` on timeout despite its name, which is easy to misuse outside the current call site.

The scan executor loop spawns per-command tasks inside a dedicated runtime and drops the runtime from within itself using `block_in_place`; shutdown semantics are intentionally asynchronous. The queue is large (`32768`) and scan commands hold work tokens, so prolonged scan failures can accumulate memory and pending metrics. The comments also warn not to use Tokio's blocking pool for scans because temp-file IO uses blocking conversions.

Memory-pressure handling deregisters and later restarts a region. During the backoff window, that region is absent from resolved checkpoints; global checkpoint selection therefore depends on remaining observed regions and `min_ts`. Correctness relies on later checkpoint-based rescan covering the gap.

## Test Signals
Tests cover retry and ordering behavior through a `Suite` with in-memory region provider, dummy scheduler, metadata store, router, and scan functions. `test_backoff_for_start_observe` validates capped exponential backoff. Failpoint-gated `test_message_delay_and_exit` checks executor shutdown under delayed scans. `test_basic_retry` verifies transient scan failure retries and eventual success. `test_on_high_mem` verifies deregistration, delayed restart, and region set restoration. `test_region_split_inflight` validates refresh during split. `test_unretryable_failure` covers epoch mismatch followed by refresh success. `test_always_failure_initial_scan` validates repeated retries until the simulated scan eventually succeeds.

Useful additional tests would cover scheduler send failures, metadata checkpoint lookup failure classes, multiple overlapping tasks, not-leader/region-absent stale starts, resolve timeout while phase-one scans are pending, and fatal emission after `TRY_START_OBSERVE_MAX_RETRY_TIME`.
