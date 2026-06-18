# sources/storage-engines/tikv/src/server/gc_worker/gc_manager.rs

## Purpose

This file implements the classic automatic GC manager. It polls PD for the GC safe point, tracks a shared safe-point atomic used by compaction filters, and when compaction-filter GC is not allowed, scans local leader regions and schedules `GcTask::Gc` work on the GC worker.

## Important APIs, Types, And Functions

- `AutoGcConfig<S, R>` contains safe point provider, region info provider, local store ID, polling interval, aggressive safe-point checking flag, and an optional post-round callback for tests.
- `GcManagerContext` owns stop-signal handling and exposes `sleep_or_stop` and `check_stopped`.
- `GcManagerState` maps internal state to metric tags (`initializing`, `idle`, `working`).
- `GcManagerHandle::stop` synchronously signals and joins the manager thread.
- `GcManager<S, R, E>` owns config, shared safe point, last safe-point check time, GC worker scheduler, stop context, config tracker, feature gate, and maximum concurrent tasks.
- `initialize` resets safe point to zero and tries to load an initial PD safe point without triggering immediate GC.
- `wait_for_next_safe_point` sleeps until the safe point advances.
- `try_update_safe_point` enforces monotonic safe points, updates the atomic, and emits safe-point metrics.
- `gc_a_round` scans regions, schedules bounded concurrent GC tasks, and rewinds when the safe point advances mid-round.
- `get_next_gc_context` uses `RegionInfoProvider::seek_region` and filters regions by local peer.

## Control Flow

`start` initializes state, installs a stop receiver, and spawns the manager thread. The main loop resets processed-region metrics, waits for a safe-point advance, and only runs range GC if `is_compaction_filter_allowed` is false. During a GC round it scans regions in key order, checks stop signals and compaction-filter eligibility, periodically refreshes the safe point, and schedules region GC tasks with callbacks that decrement a shared in-flight counter. If the safe point changes after progress has moved beyond the beginning, it finishes to the end, rewinds to the beginning, and continues until reaching the key where the new safe point was observed.

## State And Persistence Behavior

The manager persists no data itself. It stores the latest safe point in an `Arc<AtomicU64>` shared with compaction filter initialization. Region GC effects are delegated to `GcRunner` via scheduled tasks. Metrics track manager status and processed scanned/GCed regions. The concurrency controller is in-memory `Mutex<usize>` plus `Condvar`.

## Dependencies And Integration Points

The manager integrates `GcSafePointProvider` implementations such as PD clients, `RegionInfoProvider`, `Scheduler<GcTask<E>>`, feature gates, `GcWorkerConfigManager`, GC metrics, and `schedule_gc`. It is created by `GcWorker::start_auto_gc` after compaction-filter context initialization.

## Risks

- A lower safe point than the current one panics, assuming PD monotonicity.
- `max_concurrent_tasks - 1` can underflow if constructed with zero, though config validation and constructor callers are expected to prevent zero threads.
- If schedule fails because the worker is too busy, the callback path avoids decrementing in-flight count; this is intentional but easy to break when adding callback-bearing tasks.
- Region-provider callback or channel failure makes region scanning stop for that path.
- When compaction filter becomes allowed mid-round, `gc_a_round` exits early and relies on compaction-filter GC thereafter.

## Test Signals

Tests cover safe-point updates and waiting, initialization behavior, automatic GC without rewind, multiple rewind scenarios across bounded and unbounded region ranges, and worker-full scheduling via failpoint. Test utilities use mock safe-point and region providers plus a mock runner that records scheduled tasks.
