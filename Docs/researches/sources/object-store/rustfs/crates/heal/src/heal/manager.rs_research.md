<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/manager.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/manager.rs

## Purpose

`manager.rs` is the central heal scheduler and admission controller. It owns the priority queue, active task map, completed-task status cache, global heal configuration/state/statistics, background queue scheduler, and automatic disk scanner for unformatted local disks. It turns `HealRequest` submissions into `HealTask::execute` calls while enforcing queue capacity, deduplication, priority ordering, optional displacement, and per-erasure-set bulkheads.

## Important APIs, types, and functions

- `PriorityHealQueue` wraps a `BinaryHeap<PriorityQueueItem>`, FIFO sequence number, and dedup-key reference counts.
- `PriorityQueueItem` orders higher `HealPriority` first and lower sequence first within equal priority.
- `QueuePushOutcome` distinguishes accepted versus merged duplicate pushes.
- `CompletedHealStatus` stores recent completed task type/status/result items plus completion time.
- `HealTaskReport` is the public report used by channel queries.
- `HealConfig` reads environment-backed defaults for auto heal, intervals, concurrency, queue size, low-priority merge/drop policy, event-driven scheduler, set bulkhead, and page parallel flags.
- `HealState` stores manager runtime flags and cumulative counters.
- `HealManager` owns config, state, active tasks, queue, completed cache, storage, cancellation token, statistics, and scheduler notify handle.
- Public methods include `new`, `start`, `stop`, `submit_heal_request`, status/report/progress getters, `cancel_task`, `cancel_tasks_for_path`, statistics/count getters, and queue length.
- Background methods include `start_scheduler`, `start_auto_disk_scanner`, and static `process_heal_queue`.
- Helpers include `heal_type_matches_path`, metric publishers, per-set scheduling helpers, completed-status pruning, and active-running metric updates.

## Control flow

Submission first reads config and locks the queue. Non-forced duplicate dedup keys are merged, except low-priority duplicates can be policy-dropped when low-priority merge is disabled. If the queue is full and the request is not forced, higher-priority requests can displace one lower-priority queued request; otherwise low priority may be dropped or the request is reported full. Accepted requests are pushed into the heap, queue length metrics are updated, and the scheduler is notified when event-driven scheduling is enabled.

`start` marks the manager running, spawns the scheduler, and spawns the auto disk scanner. `stop` cancels the manager cancellation token, cancels all active tasks, clears active/completed state, resets metrics, and marks the manager stopped. The same cancellation token is used by background loops, so a stopped manager instance is not reusable without constructing a new token.

The scheduler loop wakes on cancellation, notify, or interval. `process_heal_queue` checks global active capacity, locks the queue, optionally skips erasure-set requests whose set already hit `max_concurrent_per_set`, converts selected requests into `Arc<HealTask>`, inserts them into `active_heals`, and spawns each task. When a task finishes, the spawned future removes it from active state, inserts a pruned completed-status entry, updates success/failure/running statistics, updates running metrics, and notifies the scheduler again.

The auto disk scanner periodically inspects `GLOBAL_LOCAL_DISK_MAP`; unformatted disks become candidates. It lists buckets through storage, formats endpoint pool/set into a set disk id, skips duplicate queued/active erasure-set heals, and enqueues normal-priority erasure-set requests directly into the queue.

Status paths check active tasks first, queued request ids second, and recent completed statuses third. Path-bound variants require the task's heal type to match the supplied path; if another task exists for the path, an unknown token returns `InvalidClientToken`. Completed statuses are retained for `KEEP_HEAL_TASK_STATUS_DURATION` of ten minutes.

Cancellation by task id cancels active tasks or removes queued requests. Cancellation by path cancels all matching active tasks and queued requests and errors only if no match exists; channel-level path cancel converts unknown path to success.

## State and persistence behavior

Manager state is in memory. Active tasks and the queue are protected by `tokio::Mutex`; config/state/statistics use `RwLock`. Completed statuses are in-memory and pruned after ten minutes. Queue dedup state is maintained as reference counts so forced duplicates reserve the key until all queued copies are popped or removed.

Persistent healing effects are delegated to `HealTask` and storage implementations, and erasure-set resume persistence is handled outside this file. The auto scanner derives candidates from the global local disk map and storage bucket listing, but does not persist its own cursor. Metrics are pushed through crate-level setters plus `metrics::counter` and `metrics::gauge`.

## Dependencies and integration points

The manager integrates with `HealStorageAPI`, `HealTask`, `HealRequest`, `HealType`, `HealOptions`, `HealPriority`, and `HealTaskStatus`. It depends on `rustfs_common::heal_channel` for admission result/drop reason, `rustfs_ecstore` disk APIs and `GLOBAL_LOCAL_DISK_MAP` for auto scanning, `rustfs_config`/`rustfs_utils` for configuration, `tokio` primitives for async scheduling, and `metrics`/`tracing` for observability. Channel queries and cancels rely on `get_task_report_for_path`, `get_task_status_for_path`, and path matching semantics here.

## Risks and edge cases

- `stop` cancels the manager-level token used by scheduler and scanner. There is no token reset on `start`, so restarting the same manager may immediately stop background loops.
- The scheduler holds `active_heals_guard` while locking the queue and while spawning tasks. Other paths generally avoid reverse lock order, and the auto scanner comment explicitly uses queue-first then active to avoid deadlock.
- Forced requests bypass duplicate and full-queue admission, so queue length can exceed configured capacity.
- Completed statuses are in-memory only and expire after ten minutes; clients polling late will see not found, which the channel may translate to finished.
- Auto scanner pushes directly into `PriorityHealQueue` rather than calling `submit_heal_request`, so it shares queue dedup but bypasses full-queue admission policy and queue-pressure logging.
- Per-set bulkhead only applies to `HealType::ErasureSet`; object requests with pool/set options use labels for metrics but are always schedulable.
- Low-priority duplicate policy can drop a duplicate request even though an equivalent queued request exists; clients must interpret `Dropped(PolicyDropped)`.
- Displacement removes a lower-priority request without sending that displaced request's client a direct failure response unless the client later polls and sees task not found.

## Test signals

Tests cover queue priority ordering, FIFO within priority, dedup key generation, erasure-set contains checks, priority statistics, empty state, bulkhead skip behavior, per-set scheduling limits, duplicate merge, queued pending status, path-token rejection, inactive path behavior, completed status/report reads, queued cancellation by id/path, full-queue low-priority drop, high-priority displacement, and forced admission behavior. Further useful tests would cover manager stop/start reuse, auto scanner full-queue behavior, event-driven wakeups, completed-status pruning timing, and task completion metric labels.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/manager.rs -->
