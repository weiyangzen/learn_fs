# sources/storage-engines/tikv/components/backup-stream/src/subscription_track.rs

## Purpose
`subscription_track.rs` implements the in-memory subscription state and resolved-ts logic for backup-stream regions. It tracks whether a region is pending initial setup or actively observed, owns the active raftstore observe handle, and wraps TiKV's resolved-ts `Resolver` with a two-phase mechanism that handles concurrent initial scan and incremental observation.

The module is the local correctness guard for checkpoint advancement. It prevents a region's checkpoint from moving beyond the initial-scan start timestamp until the scan is complete, and it buffers incremental lock/unlock events seen during phase one so lock state remains consistent once normal resolving begins.

## Important APIs, Types, And Functions
`SubscriptionTracer` is a cloneable wrapper around `Arc<DashMap<u64, SubscribeState>>` plus `Arc<TxnStatusCache>`. It provides `clear()`, `add_pending_region()`, `register_region()`, `current_regions()`, `resolve_with()`, `set_pending_if()`, `deregister_region_if()`, `try_update_region()`, `is_observing()` for tests, and `get_subscription_of()`.

`SubscribeState` is `Pending(Region)` or `Running(ActiveSubscription)`. `Pending` represents a region between start request and successful initial scan setup. `Running` contains `ActiveSubscription`, which stores region metadata, `ObserveHandle`, and `TwoPhaseResolver`. `ActiveSubscription::new()` creates a resolver with optional stable/start timestamp; `stop()` calls `ObserveHandle::stop_observing()`; `resolver()` and `handle()` expose internals to the manager.

`CheckpointType` describes why a checkpoint has its value: `MinTs`, `StartTsOfInitialScan`, or `StartTsOfTxn(Option<(TimeStamp, TxnLocks)>)`. `ResolveResult` contains region metadata, checkpoint timestamp, and checkpoint type. `ResolveResult::resolve()` asks the active subscription resolver for a timestamp and classifies the blocker.

`Ref` and `RefMut` abstract mutable references returned by `get_subscription_of()`. `ActiveSubscriptionRef` wraps a DashMap mutable ref and guarantees the entry is `Running`.

`TwoPhaseResolver` wraps `resolved_ts::Resolver`, `future_locks: Vec<FutureLock>`, and `stable_ts: Option<TimeStamp>`. Its APIs are `new()`, `in_phase_one()`, `track_phase_one_lock()`, `track_lock()`, `untrack_lock()`, `resolve()`, `resolved_ts()`, `sample_far_lock()`, and `phase_one_done()`. `FutureLock` stores buffered incremental `Lock(key, ts, generation)` and `Unlock(key)` operations while phase one is active.

## Control Flow
A region starts absent. `SubscriptionTracer::add_pending_region()` inserts `Pending(region)` if the entry is vacant and logs if a pending/running entry already exists. Once observation and scan setup starts, `register_region()` increments `TRACK_REGION`, replaces a pending entry with `Running(ActiveSubscription::new(...))`, or logs unexpected transitions for absent/running states. Replacing an already running entry decrements the counter to avoid double counting.

`resolve_with(min_ts, regions)` is called by the subscription manager after the external resolver determines which region ids are currently resolvable leaders. It builds a `HashSet` of those ids, iterates mutable subscription entries, skips pending regions, skips running regions absent from the provided id set with a metric increment, and returns `ResolveResult::resolve()` for included running regions.

`deregister_region_if()` removes pending regions directly. For running regions, it evaluates the caller predicate against the active subscription and new region, decrements `TRACK_REGION`, stops the observe handle, logs, and removes the entry only when the predicate is true. `set_pending_if()` is similar but converts a matching running entry back to pending with the old region metadata; this is used after start/scan failure to retain the placeholder for retry/refresh logic.

`try_update_region()` handles metadata-only refresh. It obtains a running subscription, compares old and new epoch versions, and if the version is unchanged replaces `subscription.meta` without resetting the resolver. A version change returns false so the manager can deregister and rescan.

`TwoPhaseResolver` starts with `stable_ts = Some(start_ts)` when an initial scan is in progress. `resolve(min_ts)` returns `min(min_ts, stable_ts)` and `resolved_ts()` returns `stable_ts`, regardless of incremental locks, while phase one is active. `track_phase_one_lock()` directly tracks locks found by the initial scan. Incremental `track_lock()` and `untrack_lock()` during phase one are appended to `future_locks` instead of mutating the resolver. `phase_one_done()` replays buffered future locks in order, clears `stable_ts`, and advances the underlying resolver to the former stable ts. After that, normal track/untrack and `resolver.resolve(min_ts, TsSource::BackupStream)` behavior applies.

## State And Persistence Behavior
All state in this file is memory-only. The durable implication is through resolved checkpoints emitted by `ResolveResult`: a lower checkpoint prevents backup metadata/global checkpoint from claiming progress that has not been safely scanned or that is blocked by an active transaction lock.

The subscription map also owns observe-handle lifetime. Removing or inactivating a running subscription calls `stop_observing()`, which tells raftstore observation to stop delivering events for that handle. Metrics state (`TRACK_REGION`) must stay balanced with Running entries.

`TwoPhaseResolver` uses an unlimited `MemoryQuota::new(usize::MAX)` internally, with a TODO to limit memory. Lock state is therefore constrained by process memory and by higher-level high-memory handling in `subscription_manager`. The transaction status cache is shared into the underlying resolver.

## Dependencies And Integration Points
This module depends on DashMap, raftstore coprocessor `ObserveHandle`, `resolved_ts::Resolver`, `TxnLocks`, `TsSource`, TiKV `TxnStatusCache`, memory quota types, `kvproto::metapb::Region`, backup-stream metrics, and utility logging helpers.

It is used by `subscription_manager` to serialize region state transitions and checkpoint calculation, by the router/event path through `TwoPhaseResolver` lock tracking while converting raft `CmdBatch` into `ApplyEvents`, and by endpoint/checkpoint code through `ResolveResult` and `CheckpointType` diagnostics.

## Risks And Edge Cases
The two-phase algorithm depends on preserving event order in `future_locks`. If incremental events are buffered out of order or phase-one scan locks are not tracked with `track_phase_one_lock()`, the resolver can retain or drop locks incorrectly. `handle_future_lock()` unwraps memory-quota errors when replaying buffered locks because the quota is currently unlimited; adding a real quota will require error handling here.

`resolve_with()` collects region ids into a set and skips pending regions. If a region stays pending for a long time, it contributes no checkpoint result; the manager relies on phase-one Running state, not Pending, to hold checkpoint back. State transition bugs that leave a region pending after observation begins can therefore affect global checkpoint calculation.

`register_region()` increments `TRACK_REGION` before inspecting the old state and then compensates only for running-to-running replacements. The accounting is subtle and must stay aligned with `clear()`, `set_pending_if()`, and `deregister_region_if()`. Unexpected absent-to-running is allowed with a warning; that path increments the metric and may be correct for tests/refresh but bypasses the intended pending placeholder.

`try_update_region()` only compares epoch version, not conf version. That matches the local refresh intent, but callers must use stronger epoch checks for destroy/stop decisions. `ActiveSubscriptionRef` relies on its constructor to avoid pending states; misuse would hit `unreachable!()`.

## Test Signals
`test_two_phase_resolver` verifies that phase-one stable ts caps resolution, future lock/unlock buffering is replayed after `phase_one_done()`, and normal incremental lock resolving works afterward. `test_delay_remove` checks that deregistration stops observation. `test_cal_checkpoint` builds multiple subscriptions covering phase-one, no-lock, finished initial scan, lock-blocked, and removed-region cases, then validates checkpoint values and `CheckpointType` classification including sampled transaction locks.

Additional useful tests would cover pending-region exclusion, `set_pending_if()` handle predicates, metric balancing under unexpected transitions, region metadata refresh with unchanged and changed epoch versions, future-lock replay order with multiple keys/generations, and memory-quota behavior if the TODO is implemented.
