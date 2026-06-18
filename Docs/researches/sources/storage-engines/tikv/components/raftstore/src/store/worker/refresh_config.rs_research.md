# sources/storage-engines/tikv/components/raftstore/src/store/worker/refresh_config.rs

## Purpose
This file implements a raftstore worker for applying runtime configuration changes to batch-system pools and async store IO components. It can resize raft and apply poller thread pools, update their max batch sizes, resize async store writer threads, and resize the snapshot generator/read future pool.

## Important APIs, Types, and Functions
`PoolController<N, C, H>` groups a `BatchRouter` with its `PoolState`. It provides `decrease_by()`, `increase_by()`, and `cleanup_poller_threads()`. `decrease_by()` sends `FsmTypes::Empty` control messages to ask pollers to exit; `increase_by()` builds new handlers/pollers and spawns named worker threads with foreground-write IO type; `cleanup_poller_threads()` joins poller threads that have reported themselves as joinable.

`WriterContoller<EK, ER, T, N>` stores `StoreWritersContext`, `StoreWriters`, and an expected writer count. It exposes getters/setters used by the runner to resize async writer threads. The name is misspelled in code as `Contoller`.

`BatchComponent` distinguishes `Store` (displayed as `raft`) and `Apply`. `Task` is the public work enum: `ScalePool(BatchComponent, usize)`, `ScaleBatchSize(BatchComponent, usize)`, `ScaleWriters(usize)`, and `ScaleAsyncReader(usize)`.

`Runner<EK, ER, AH, RH, T>` owns the writer controller, apply pool controller, raft pool controller, and snapshot generator `FuturePool`. Its resize helpers are `resize_raft_pool()`, `resize_apply_pool()`, `resize_store_writers()`, and `resize_snap_generator_read_pool()`.

## Control Flow
`Runner::new()` wraps the writer metadata/writers and both batch-system pool states into controllers. `Runnable::run()` pattern-matches tasks and dispatches to the appropriate helper.

Pool resizing reads `expected_pool_size`, updates it to the requested size, compares old and new sizes, sends empty FSMs to shrink or spawns poller threads to grow, then calls `cleanup_poller_threads()` and logs the result. If the size is unchanged, it returns early.

`increase_by()` clones thread-group properties, creates a normal-priority handler, constructs a `Poller` with the shared router/receiver/max batch settings, spawns a named thread using `spawn_wrapper`, sets the inherited thread-group properties, marks IO type as foreground write, and calls `poller.poll()`. The controller increments `id_base` after spawning so future thread names remain unique.

Store writer resizing updates the expected writer size, then calls `StoreWriters::decrease_to(size)` or `increase_to(size, writer_meta.clone())`. Local cached writers in pollers are not updated immediately; comments state each poller corrects its local cache on its next `poller.begin()`.

Snapshot generator pool resizing calls `FuturePool::scale_pool_size(size)`, then compares the requested size with `thread_count_limit()`. Out-of-bound sizes are clamped by the pool and logged as warnings; in-bound sizes are logged as resizes.

Batch-size tasks directly assign `state.max_batch_size` for the selected raft/apply pool.

## State and Persistence Behavior
All effects are in-memory process state. The file does not persist configuration. Resized pool sizes live in `PoolState.expected_pool_size`, `PoolState.max_batch_size`, `StoreWriters` internal thread state, `WriterContoller.expected_writers_size`, and the `FuturePool` worker count.

Shrinking a batch-system pool is cooperative: empty FSM messages cause pollers to drop, and poller drop records thread IDs into `joinable_workers`. `cleanup_poller_threads()` then joins and removes those handles from `workers`. The lock order is intentionally `workers` then `joinable_workers` to avoid deadlock with batch-system shutdown.

Store writer resize state can be temporarily inconsistent because pollers keep local cached writers until the next poller begin cycle. The explicit expected size records the intended target even if `increase_to()` or `decrease_to()` logs an error.

## Dependencies and Integration Points
The code integrates with `batch_system` types (`BatchRouter`, `Fsm`, `HandlerBuilder`, `Poller`, `PoolState`, `Priority`) and concrete raftstore FSMs (`PeerFsm`, `StoreFsm`, `ApplyFsm`, `ControlFsm`). It depends on `StoreWriters` and `StoreWritersContext` from async IO write support, `RaftRouter` as persisted notifier, `Transport`, and `FuturePool` from `tikv_util::yatp_pool`.

Thread behavior integrates with TiKV thread naming (`thd_name!`), `StdThreadBuildWrapper`, thread-group property propagation, and `file_system::set_io_type(IoType::ForegroundWrite)`.

Operationally, tasks are produced by configuration-refresh code elsewhere in raftstore when runtime config values such as raft/apply pool size, max batch size, store IO pool size, or snapshot generator pool size change.

## Risks and Edge Cases
The pool shrink path depends on pollers processing `FsmTypes::Empty`; if a poller is stuck, cleanup may not find/join it promptly. The explicit lock-order comment indicates deadlock risk if shutdown and cleanup acquire locks differently.

`expected_pool_size` and `expected_writers_size` are updated before resize operations can fail. If thread spawning panics or writer resize returns an error, the recorded expected size can diverge from actual workers. `increase_by()` unwraps thread spawn failures, so OS thread creation failure panics the worker.

Changing `max_batch_size` is immediate shared state mutation and does not coordinate with already-running poll loops beyond their normal state access. Snapshot generator pool scaling is advisory and clamped by its configured min/max; warning text mentions "apply pool" even though it is resizing the async reader/snapshot pool.

Thread names for newly increased pools use the local loop index plus `id_base`; after multiple resizes IDs remain unique but not dense. Store writer resizing has an expected transient period where pollers still use stale cached writer handles.

## Test Signals
This file has no local `#[cfg(test)]` module. Useful tests would construct small batch-system pools and verify grow/shrink updates expected sizes, joins exiting pollers without deadlock, preserves thread naming/id base, updates max batch size for raft versus apply independently, handles no-op resize, and logs or clamps out-of-bound snapshot pool sizes.

For writer resizing, tests should verify `increase_to()` receives cloned writer metadata, `decrease_to()` is called with the target size, expected writer size behavior on errors, and poller-local writer cache refresh on subsequent poller begin cycles in integration tests.
