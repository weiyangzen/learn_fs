# sources/storage-engines/tikv/components/raftstore-v2/src/fsm/apply.rs

Purpose: Defines the apply FSM wrapper and scheduler that execute committed raft entries and apply-side tasks for one peer on an async future pool.

Important APIs/types/functions: `ApplyResReporter` abstracts reporting apply results and catch-up log redirects back to a peer mailbox. `ApplyScheduler` wraps a future MPSC sender and exposes `send`. `ApplyFsm<EK,R>` owns a `raft::Apply<EK,R>` and an `ApplyTask` receiver. `ApplyFsm::new` builds the underlying `Apply` with config, peer/region state, tablet registry, read/tablet schedulers, high-priority pool, flush/SST state, optional log recovery, buckets, importer, coprocessor host, and logger. `handle_all_tasks` is the async task loop.

Control flow: The loop waits for either an apply task or a 10-second idle timeout. On idle it releases apply memory, then waits for the next task. For each task it calls `on_start_apply`, handles committed entries, snapshots, unsafe writes, manual flush, bucket refresh, or capture-apply tasks, then `maybe_flush`. It drains immediately available tasks with `try_recv` before doing a final `flush` and `maybe_reschedule`.

State and persistence behavior: Persistence is delegated to `Apply`: applying entries writes to tablets/raft state through engine abstractions, flush state, SST apply state, and result reporting. This wrapper owns the task channel and controls batching/flush cadence, but not the persistent data structures directly.

Dependencies and integration points: It connects `batch_system` mailboxes, `tikv_util::mpsc::future`, raftstore read tasks, tablet workers, SST importer, PD bucket stats, and raftstore-v2 router `ApplyTask`/`ApplyRes`. Peer FSMs create and schedule apply FSMs during startup and raft ready handling.

Risks: `ApplyScheduler::send` unwraps, so sending after receiver shutdown panics. Idle memory release depends on timeout behavior. Long task bursts can defer final flush until the local queue drains. Correctness depends on `Apply::maybe_flush` and `flush` preserving apply order.

Test signals: The file has a `before_handle_tasks` failpoint. Behavioral coverage is expected through raftstore-v2 integration tests for committed-entry apply, snapshot generation, manual flush, bucket refresh, and shutdown.
