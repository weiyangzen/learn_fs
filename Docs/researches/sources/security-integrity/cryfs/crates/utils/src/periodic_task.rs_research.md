# sources/security-integrity/cryfs/crates/utils/src/periodic_task.rs

Purpose: Implements an async periodic background task that runs a user-supplied async closure after each interval while the owning `PeriodicTask` is alive. It integrates with the crate's `AsyncDropGuard` cleanup pattern.

Important APIs and types: `PeriodicTask::spawn(name, interval, task)` returns `AsyncDropGuard<PeriodicTask>`. `PeriodicTask::terminate` cancels future iterations and awaits the join handle. The private `PeriodicTaskImplTerminate` trait type-erases cancellation and task naming; `PeriodicTaskImpl<T, F>` stores the task closure, interval, name, and `CancellationToken`.

Control flow: `spawn` builds an `Arc<PeriodicTaskImpl>`, starts `_run`, and stores the join handle. `_run` loops in a tokio task with `select!` between `CancellationToken::cancelled()` and `tokio::time::sleep(interval)`. On each sleep, it awaits the user task, logs `Err`, and continues. `terminate` cancels the token and awaits the join handle once. `AsyncDrop::async_drop_impl` delegates to `terminate`.

State and persistence behavior: State is in memory only: cancellation token, join handle, task closure, and name. Termination does not abort an already-running iteration; it only prevents future sleeps/tasks after the current await completes. If `terminate` already joined, `join_handle` is `None` and later cleanup is idempotent.

Dependencies and integration points: Uses `tokio` tasks, `tokio::select!`, `tokio_util::sync::CancellationToken`, `anyhow::Result`, `async_trait`, the crate `async_drop` module, and `log`. Consumers must run on a tokio runtime, and docs warn that synchronous drop/blocking async-drop behavior can deadlock on a single-thread runtime.

Risks: Task errors are logged but not surfaced to the owner. A panic inside the spawned task ends the background task; because termination awaits the join handle only when cleanup happens, panics can be delayed or under-tested. Long-running task iterations delay shutdown. The closure is `Fn + Sync` rather than `FnMut`, so mutable periodic state needs interior mutability.

Test signals: Tokio tests cover empty tasks, repeated execution, explicit termination stopping later runs, async drop stopping later runs, and current behavior for erroring or panicking task closures.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/periodic_task.rs` completely for this pass (263 lines, 9194 bytes).
