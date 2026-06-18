# sources/storage-engines/tikv/src/read_pool.rs

## Purpose

`read_pool.rs` builds and manages TiKV's read execution pools. It supports the older three-pool `FuturePools` mode split by request priority and the newer unified YATP pool (`ReadPool::Yatp`) that combines priority scheduling, resource-control admission, task eviction, metrics, thread-local engine setup, and online resizing.

The file is on the hot read path. Callers use `ReadPool::handle()` to get a cheap `ReadPoolHandle`, then enqueue read futures through `spawn` or `spawn_handle`. The unified mode is also used by server busy checks because it tracks task queue depth and an EWMA of task poll duration to estimate wait time.

## Important APIs, types, and functions

`ReadPool` owns the actual pools. `FuturePools` contains high, normal, and low `FuturePool`s. `Yatp` owns a `yatp::ThreadPool<TaskCell>`, per-resource-priority running-task gauges, a thread-count gauge, max-task accounting, optional `ResourceController` and `ResourceGroupManager`, and a shared `TimeSliceInspector`.

`ReadPoolHandle` is the cloneable execution interface. `spawn` selects a `FuturePool` by `CommandPri` or constructs a YATP `TaskCell` with multilevel scheduling metadata. `spawn_handle` wraps `spawn` with a oneshot channel so callers can await a task result. `scale_pool_size`, `set_max_tasks_per_worker`, `get_queue_size_per_worker`, and `check_busy_threshold` are used by config management and request admission.

`admission_and_enqueue` is the key unified-pool enqueue path. It asks the resource group manager for an admission decision before any capacity or eviction logic. Rejected tasks return `ReadPoolError::Rejected`; delayed tasks sleep outside the pool, with a warning for delayed high-priority reads. After admission, it checks `running_tasks` against `max_tasks`; if resource control is enabled it tries `remote.try_evict_lowest(estimated_priority)` and decrements the evicted task's priority gauge, otherwise it returns `UnifiedReadPoolFull`.

`TimeSliceInspector` samples YATP `TASK_POLL_DURATION` histograms across scheduling levels and maintains an atomic EWMA in nanoseconds. `get_estimated_wait_duration` multiplies EWMA by queue size per worker, and `check_busy_threshold` converts excessive wait estimates into `errorpb::ServerIsBusy`.

`build_yatp_read_pool` and `build_yatp_read_pool_with_name` configure the unified pool. They set thread counts from `UnifiedReadPoolConfig`, install TLS storage engine state in `after_start`, set foreground-read IO type, destroy TLS engine state in `before_stop`, select priority-pool vs multilevel-pool depending on resource control, register metrics, and preserve optional task wait metrics.

`ReadPoolCpuTimeTracker`, `ReadPoolConfigRunner`, and `ReadPoolConfigManager` implement online pool resizing. The runner receives config tasks for max thread count, auto-adjust, max tasks per worker, and CPU threshold, and also wakes every `READ_POOL_THREAD_CHECK_DURATION` to auto-adjust thread count.

`ReadPoolError` distinguishes old `FuturePoolFull`, unified full, resource-control rejection, and oneshot cancellation.

## Control flow

In legacy mode, `spawn` maps `CommandPri::{High,Normal,Low}` directly to one of three `FuturePool`s and returns a ready future containing the spawn result.

In unified mode, `spawn` derives `TaskPriority` from `TaskMetadata::override_priority`, maps background resource-limited jobs to low scheduling level, maps high/low `CommandPri` to fixed YATP levels, and leaves normal foreground work for multilevel scheduling. It stores metadata in `Extras`, wraps the future in `ControlledFuture` and `with_resource_limiter` when resource control is enabled, and ensures the running-task gauge is decremented when the future completes. The async `admission_and_enqueue` then admits, optionally delays, evicts if allowed, increments the gauge, and calls `remote.spawn`.

The resize path is driven by `ReadPoolConfigManager::dispatch` and timer callbacks. Direct config changes schedule a `Task`; `ReadPoolConfigRunner::run` applies the new core size, auto-adjust flag, max-tasks-per-worker, or CPU threshold. Timer callbacks call `adjust_pool_size`, which measures read-pool CPU usage from Linux thread stats, YATP task-handling time from metrics, current queued/running tasks, and process CPU. It scales in when CPU-threshold pressure is high, scales back out toward the configured core count when read-pool CPU is below threshold, and otherwise applies thread-utilization scale-in/out rules bounded by min/core/max counts.

## State and persistence behavior

This file does not persist user data. Its state is in-memory pool state: running-task gauges, thread counts, max-task limits, EWMA samples, previous CPU/time counters, and scheduled config tasks. Persistent effects are indirect: read futures execute storage work using TLS engine handles installed on read-pool worker threads, and resource-control debt/accounting can be updated by `ControlledFuture` and `with_resource_limiter`.

Metrics are Prometheus state: `tikv_unified_read_pool_running_tasks`, `tikv_unified_read_pool_thread_count`, and `tikv_unified_read_pool_evicted_tasks`. The task-poll histogram is supplied by YATP.

## Dependencies and integration points

The pool integrates with `yatp`, `tikv_util::yatp_pool`, `resource_control`, `kvproto::kvrpcpb::CommandPri`, `tikv_util::resource_control::TaskMetadata`, `file_system::set_io_type`, storage engine TLS helpers, `FlowStatsReporter` metric flushing, online config through `ConfigManager`, and `tikv_util::worker::{Worker,Scheduler}`.

Server-level callers depend on `check_busy_threshold` to reject requests when estimated queueing delay is too high. The config subsystem depends on `ReadPoolConfigManager` to apply online changes under the `"unified"` config module.

## Risks and edge cases

Admission is intentionally before eviction; changing that order can let a delayed or rejected task evict already queued work. Running-task gauges must stay balanced across normal completion and eviction; leaked increments would make the pool permanently look full. `get_queue_size_per_worker` divides by pool size, so the unified pool must never be scaled to zero. CPU-based resizing depends on thread-name matching and Linux thread stats, so renamed worker threads or platform gaps can disable accurate CPU control. The YATP task-poll EWMA is a coarse cross-level average; it can over- or under-estimate specific priority classes.

`scale_pool_size` recalculates `max_tasks` using the previous per-worker capacity. A bad current `pool_size` or unexpected zero value would distort capacity. `ProcessStat::cur_proc_stat().unwrap()` in config manager construction assumes process-stat availability.

## Test signals

Tests cover unified-pool full behavior, manual scale up/down, high-priority eviction, EWMA calculation, CPU-threshold config shape, CPU-threshold scale-in/out behavior, task-poll metrics, and reset notification when auto-adjust is disabled. The eviction test explicitly verifies resource-group priority based eviction when the pool is full. These tests are focused on in-process behavior and metrics; they do not prove production thread-stat accuracy across platforms.
