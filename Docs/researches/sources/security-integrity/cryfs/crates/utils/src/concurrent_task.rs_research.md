# sources/security-integrity/cryfs/crates/utils/src/concurrent_task.rs

Purpose: wrapper around `tokio::spawn` that makes forgetting to await a spawned task a hard failure.

Important APIs/types/functions: `ConcurrentTask<T>` stores `ManuallyDrop<JoinHandle<T>>`; `spawn` creates it; `await_task(self)` consumes the wrapper and returns the join handle future.

Control flow: consuming `await_task` uses `ManuallyDrop::take` so `Drop` does not run. If the wrapper is dropped directly, its `Drop` implementation contains a const panic message.

State/persistence: holds one Tokio join handle; task state lives in Tokio runtime.

Dependencies/integration: useful for structured concurrency in async code.

Risks: Drop panic is severe and can abort if it occurs during unwinding. The comment says compile-time error, but enforcement is via `#[must_use]` on returned future plus runtime/drop panic behavior.

Test signals: tokio test spawns a task, awaits it, and checks result.
