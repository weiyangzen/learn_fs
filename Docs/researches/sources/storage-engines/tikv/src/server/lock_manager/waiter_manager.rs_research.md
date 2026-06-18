# sources/storage-engines/tikv/src/server/lock_manager/waiter_manager.rs

Purpose: manages in-memory lock waiters for pessimistic transactions, delivering callbacks when locks are released, waits time out, wait-for targets change, or deadlocks are detected.

Important APIs/types/functions: `Delay` wraps `tokio_timer::Delay` with cancellation/reset; `Task` enumerates waiter operations; `Waiter` owns transaction wait context and cancellation methods; `WaitTable` indexes waiters by token and `(lock_hash, waiter_ts)`; `Scheduler` exposes task helpers; `WaiterManager` implements `FutureRunnable<Task>`.

Control flow: `Task::WaitFor` normalizes deadline, creates a `Waiter`, inserts it into `WaitTable`, and spawns its timeout future. Timeout removes the waiter, returns `KeyIsLocked`, and asks detector to clean the wait edge. Explicit removal cancels without error and also cleans the detector. Updates replace wait info, track last update time, and for non-first-lock allowed-conflict waits, clean old detector edges and register new detect edges. Deadlock tasks remove the matching waiter and return an MVCC deadlock error.

State and persistence: all waiters are memory-only. `WaitTable` maintains two maps plus shared `waiter_count`. Metrics record waiter lifetime and task counts. No durable state exists; lost state results in timeout/retry behavior at higher layers.

Dependencies and integration: depends on global timer handle, tracker metrics, storage lock-manager types, MVCC/txn errors, detector scheduler, and lock-manager metrics. It is started by `lock_manager/mod.rs`.

Risks: delay cancellation completes at arbitrary time, so removal paths rely on taking the waiter atomically from the table to avoid double callback. The compatibility index by `(hash, waiter_ts)` assumes one relevant waiter per hash/transaction pair. Update logic has explicit caveats for future shared-lock shrink behavior.

Test signals: tests cover delay timeout/reset/cancel, waiter timeout/deadlock callbacks, wait-table add/remove/count/export, default/custom/max timeout behavior, deadlock handling, and `duration_to_last_update_ms`.
