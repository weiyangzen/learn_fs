# sources/storage-engines/tikv/components/backup-stream/src/endpoint.rs

## Purpose
`endpoint.rs` is the central actor for TiKV backup stream execution. It wires metadata watching, raftstore observation, initial scan scheduling, event routing, flush execution, checkpoint management, task pause/resume, and fatal-error reporting into one `Runnable` endpoint driven by `Task` messages.

## Important APIs, types, and functions
- `Endpoint<S, R, E, PDC>` owns `MetadataClient`, the internal `Scheduler<Task>`, a `Router` for temporary file/event handling, `BackupStreamObserver`, a Tokio runtime, `RegionSubscriptionManager` sender, PD client, `CheckpointManager`, and runtime state such as `last_flush_ts`, failover time, flush waiters, and abort handles.
- `Endpoint::new` constructs the runtime, starts periodic flush ticks, starts task and pause watchers, initializes memory/rate/concurrency controls for initial scans, starts region subscription management, starts checkpoint subscription management, and starts the min-ts worker.
- `Task`, `TaskOp`, `ObserveOp`, `RegionCheckpointOperation`, `RegionSet`, and `FlushResult` form the message protocol for the actor and its collaborators.
- `BackupStreamResolver` abstracts leader resolution for raftstore v1, raftstore v2, and tests.

## Control flow
Startup calls `start_and_watch_tasks`, which repeatedly loads metadata tasks until success, schedules active tasks, then spawns task and pause watch loops from the returned revision. Add/remove/pause/resume events become `Task::WatchTask`. Registering a task loads its ranges, registers them in the router, stores them in the observer range set, and initializes leader regions through `ObserveOp::Start`.

Raftstore command batches enter as `Task::BatchEvent`; `record_batch` checks that the region subscription and PITR handle are current, updates the two-phase resolver, converts the batch into `ApplyEvents`, and `backup_batch` asynchronously sends those events to `Router::on_events`. Out-of-quota events tell the region operator to handle high memory pressure, while stale observation is ignored.

Flushes are driven either by router ticks or explicit force flushes. `prepare_min_ts_and_flush_ts` obtains PD TSO and global min lock ts, falls back to a local monotonic flush ts only after at least one successful TSO, and calls `ObserveOp::ResolveRegions`. `on_exec_flush` freezes checkpoint manager state and runs `do_flush`, whose flush observer can rewrite resolved ts before router flush, then persists progress via the checkpoint observer.

## State and persistence behavior
Durable state is mainly delegated to metadata and PD: task info, ranges, pause markers, last errors, store checkpoints, and PD service safe points. Fatal errors call `on_fatal_error_of_task`, compute a safe point from global progress, set a per-store pause guard with a 24 hour TTL, write V2 pause JSON and last error metadata, then unload the task locally. Runtime-only state includes observed ranges, subscriptions, checkpoint manager state, flush waiters, last flush ts, semaphore capacity, and abort handles.

## Dependencies and integration points
This file integrates `MetadataClient`, `Router`, `BackupStreamObserver`, `RegionSubscriptionManager`, `InitialDataLoader`, `CheckpointManager`, `PdClient`, raftstore CDC handles, resolved-ts leadership resolution, `ConcurrencyManager`, and many backup stream metrics. It is the module re-exported by `lib.rs` for endpoint construction and external task/checkpoint operations.

## Risks and edge cases
- PD/metadata unavailability affects task watching, fatal error reporting, and TSO preparation; retries exist for watch startup and fatal error reporting, but skipped flushes can delay progress.
- `last_flush_ts` fallback is deliberately limited to avoid inventing a first timestamp without PD.
- The endpoint currently clears all observer ranges and subscriptions on unload because only one concurrent task is supported.
- Watch loops update `revision_new` by querying current revision after each event; gaps or repeated reconnects rely on store watch semantics.
- `on_force_flush` replaces any existing waiter for a task and reports an abort error to the older waiter.

## Test signals
This file has no local test module, but is exercised through observer, metadata, event loader, subscription manager, checkpoint manager, and service tests. Failpoints cover loading task ranges, flush delay, fatal error upload, and checkpoint update sleep paths.
