# sources/security-integrity/cryfs/crates/check/src/task_queue.rs

Purpose: This module provides a small recursive async task queue with bounded concurrent execution. The runner uses it to traverse blob and node trees while allowing tasks to spawn children.

Important APIs and flow: `run_to_completion(max_concurrency, initial_task)` creates an unbounded channel of boxed futures, spawns the initial task, wraps the receiver as a stream, and runs futures with `buffer_unordered(max_concurrency)` until the sender graph drains or an error occurs. `TaskSpawner::spawn` passes a cloned spawner into each future factory and sends the boxed future.

State and persistence: Queue state is in-memory channel state. It has no persistence and no cancellation ledger beyond stream error propagation.

Dependencies and integration: It uses `futures`, `tokio::sync::mpsc::unbounded_channel`, and `tokio_stream::wrappers::UnboundedReceiverStream`. `RecoverRunner` uses it for recursive traversal with `CheckError` or `anyhow::Error` style errors.

Risks and test signals: The channel is unbounded, so very broad trees can enqueue many futures even though execution is bounded. Tests cover spawning 100 direct tasks, 100 recursive tasks, and propagation of an error from a recursive task.
