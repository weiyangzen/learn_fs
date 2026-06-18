# sources/object-store/rustfs/crates/ecstore/src/batch_processor.rs

Purpose: provides reusable async batch execution utilities with concurrency caps and quorum-style early return.

Important APIs and types: `AsyncBatchProcessor` stores `max_concurrent`. `execute_batch` accepts a vector of futures returning disk `Result<T>`, runs them under a Tokio semaphore in a `JoinSet`, and returns results in original task order. `execute_batch_with_quorum` returns once `required_successes` have completed successfully or once quorum becomes impossible. `GlobalBatchProcessors` exposes read, write, and metadata processors with fixed concurrency levels 16, 8, and 12. `get_global_processors` initializes a `OnceLock`.

Control flow: all tasks are spawned immediately, but semaphore permits limit active work. Join results are collected as tasks finish; panics and semaphore errors are logged and converted to failures where possible.

State and persistence: only process-local singleton state; no durable persistence.

Dependencies and integration points: uses `crate::disk::error::{Error, Result}`, Tokio `JoinSet` and `Semaphore`, and is intended for disk/storage fan-out paths.

Risks: `execute_batch_with_quorum` returns without explicitly aborting slow spawned tasks; dropping `JoinSet` aborts remaining tasks, so callers must tolerate cancellation. `max_concurrent == 0` would deadlock tasks waiting for permits.

Test signals: unit tests cover ordered success, mixed errors, quorum success, early return before slow tail, and early failure once quorum is impossible.
