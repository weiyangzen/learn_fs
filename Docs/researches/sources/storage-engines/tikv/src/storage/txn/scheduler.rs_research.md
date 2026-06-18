# sources/storage-engines/tikv/src/storage/txn/scheduler.rs

## Purpose
`scheduler.rs` implements `TxnScheduler`, the core transaction command scheduler for TiKV storage. It receives client commands, applies admission and flow-control checks, serializes conflicting command-level access through latches, obtains snapshots, dispatches read/write command processing to worker futures, coordinates lock-wait/resume behavior for pessimistic transactions, submits writes to the engine/raftstore, and delivers callbacks.

## Important APIs, types, and functions
`TxnScheduler<E, L>` is the public scheduler handle. `TxnSchedulerInner<L>` contains sharded task slots, command ID allocation, `Latches`, `SchedPool`, resource-control handles, write-byte counters, flow controller, lock manager, concurrency manager, dynamic pessimistic-lock flags, lock-wait queues, quota limiter, feature gate, transaction status cache, and scheduler memory quota.

`TaskContext` is the in-flight command record. It stores the optional `Task`, latch `Lock`, callback, optional early process result, resumable lock-wait entries woken by released locks, ownership bit, write-byte estimate, command tag, latch timer, and command timer. The atomic `owned` bit prevents races among normal processing, fail-fast precheck, deadline timeout, and early callback paths.

`SchedulerTaskCallback` wraps either a normal storage callback or per-key pessimistic-lock callbacks. `CmdTimer` and `SchedulerDetails` record command and stage timings. `PessimisticLockMode` selects sync, pipelined, or in-memory pessimistic-lock behavior. `get_raw_ext` obtains causal timestamps and key guards for raw compare-and-swap or atomic store commands when API v2 causal-ts support is available.

Major scheduler methods include `run_cmd`, `schedule_command`, `execute`, `process`, `process_read`, `process_write`, `handle_task`, `handle_non_persistent_write_result`, `handle_flow_control`, `handle_async_write`, `on_read_finished`, `on_write_finished`, `finish_with_err`, lock-wait helpers, and wake-up helpers.

## Control flow
`run_cmd` is the command entry point. It first rejects writes when scheduler pending bytes or flow-controller drop logic says the store is too busy. It then asks resource-control admission whether to reject or delay. Delayed commands are re-submitted after sleeping without holding latches. Accepted commands receive a new command ID and are wrapped in `Task::allocate`, which charges scheduler memory quota.

`schedule_command` inserts a `TaskContext`, records metrics and request-tracker fields, and tries to acquire the command's generated latches. If all required latches are acquired, it calls `execute`. If not, it starts fail-fast/precheck/deadline monitoring. The deadline path can take the callback early through `try_own_and_take_cb`; the task remains queued until latch wake-up so latches can be released consistently later.

`execute` installs the tracker token in TLS, starts a tracked future on the scheduler pool, gets an engine snapshot, copies snapshot term and extra operation metadata into the command, claims task ownership, and calls `process`. Read commands execute `Task::process_read`, collect statistics, and finish through `on_read_finished`. Write commands execute `handle_task`, which builds `WriteContext`, gets raw causal-ts extensions if needed, calls the command's write processor, accounts read/write quota samples, and returns `WriteResult`.

`process_write` checks deadlines and duplicate-lock debug conditions, handles non-persistent effects, then either finishes without raftstore persistence or proceeds to flow control and `handle_async_write`. `handle_async_write` configures disk-full behavior and response subscriptions, marks in-memory pessimistic locks as deleted before submitting lock-CF writes, calls engine `async_write`, performs early response on committed/proposed events for async-apply-prewrite or pipelined pessimistic locking, and performs final cleanup on `Finished`.

Completion handlers dequeue `TaskContext`, update status cache for known committed transactions, execute callbacks, wake pessimistic lock waiters when released locks allow it, put back deferred wait entries if needed, and release latches. `release_latches` wakes queued command IDs and `try_to_wake_up` reacquires latches or fails expired tasks through the pool to avoid recursive stack growth.

## State and persistence behavior
Persistent mutations are not built directly in this file; command processors produce `WriteData`, and the scheduler decides whether and when to submit it. It can avoid persistence for eligible pessimistic locks by inserting lock-CF modifies into raftstore `TxnExt` in-memory pessimistic-lock tables when feature gates and size limits allow. It can also skip immediate client waiting for persistence in pipelined or async-apply modes, but final latch release and cleanup still wait for the async write finish event.

In-memory state includes sharded task slots, latch queues, running write-byte counters, lock-wait queues, memory quota allocations, status cache inserts, and per-request tracker metrics. Flow control consumes write bytes before async write; failed writes unconsume to prevent quota exhaustion. Known transaction statuses are inserted into `TxnStatusCache` before callbacks are invoked.

## Dependencies and integration points
The scheduler sits at the center of storage integration. It depends on storage engines and snapshots, raftstore `TxnExt`, concurrency manager key guards, lock manager wait APIs, lock-wait queues, transaction command processors, MVCC errors, latches, resource metering and resource control, quota limiter, flow controller, PD query stats, tracker metrics, Yatp scheduler pool, feature gates, failpoints, and kvproto request context. It is called from higher storage service code through `TxnScheduler::run_cmd` and calls back through `StorageCallback`.

## Risks and edge cases
Correctness depends on precise ordering: wait entries are pushed to scheduler lock-wait queues before calling the lock manager so cancellation does not race with wake-up; in-memory pessimistic locks are marked deleted before raftstore submission and physically removed only after apply succeeds; early callbacks do not release latches until final write completion. Undetermined async write results panic because releasing latches would risk violating correctness, while retaining them would deadlock later transactions.

The ownership bit is essential but subtle. Races among snapshot completion, deadline timers, precheck errors, and early pipeline responses must leave exactly one callback owner. Flow-control delay checks command deadlines in a loop and must unconsume bytes on timeout. `handle_non_persistent_write_result` has special cases for lock wait, resumed lock wait, shared-lock updates, and in-memory lock eligibility. Feature-gated `InMemory` mode requires both pipelined and in-memory flags plus feature support; otherwise it falls back to pipelined or sync behavior.

Resource-control admission delay intentionally happens before latch acquisition, preventing delayed commands from blocking overlapping writers. Memory quota is charged both for command heap size in `Task::allocate` and force-charged for the spawned execution future, then freed on future completion. The debug duplicate-lock check can panic in production if enabled, so it is guarded by `ENABLE_DUP_KEY_DEBUG`.

## Test signals
The local tests cover latch serialization for read/write command classes, deadline expiration while waiting on latches, fail-fast precheck for queued commands, expired commands before pool availability, flow-control timeout and unconsume behavior, avoiding stack overflow when many expired commands wake, pessimistic-lock mode selection and feature gating, forcing shared-lock updates to persist instead of using in-memory locks, and scheduler memory-quota rejection/freeing. These tests exercise many scheduler state transitions but do not fully cover async write event ordering, lock-manager cancellation races, raw causal-ts extension failures, or resource-control dynamic priority routing.
