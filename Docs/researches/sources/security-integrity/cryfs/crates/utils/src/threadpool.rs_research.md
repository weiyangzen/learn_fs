# sources/security-integrity/cryfs/crates/utils/src/threadpool.rs

Purpose: Wraps a Rayon thread pool so CPU-bound closures can be spawned from async code and awaited through a Tokio oneshot channel.

Important APIs and types: `ThreadPool::new(name)`, `new_with_num_threads(name, num_threads)`, and `execute_job<R>(job)` form the public API. Private `num_threads` uses `std::thread::available_parallelism`.

Control flow: Construction builds a Rayon `ThreadPool` with named worker threads. `execute_job` creates a Tokio oneshot channel, spawns a FIFO Rayon job that runs the closure and sends the result, then awaits the receiver. `num_threads` logs detected parallelism or warns and falls back to 2.

State and persistence behavior: State is in memory: the Rayon pool and queued jobs. There is no persistence. Job panics cause sender drop or send failure, and the await path reports `"Thread pool task panicked"`.

Dependencies and integration points: Depends on `rayon`, `tokio::sync::oneshot`, `anyhow::Result`, `futures` in tests, and logging. It supports code paths that cannot use `tokio::task::spawn_blocking`, including tests that call it from `futures::executor::block_on`.

Risks: `execute_job` requires `'static` closures and `Send + Debug` return values. It unwraps `sender.send`, so if the receiver is dropped before completion the Rayon job panics. There is no cancellation or backpressure beyond the Rayon queue. The `Debug` bound is not used by the implementation.

Test signals: Tests cover simple/computed/string/vector returns, captured environment, sequential and concurrent jobs, shared atomics, blocking operations, pool reuse, at least one detected thread, explicit two-thread barrier parallelism, and use from `futures::executor::block_on`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/threadpool.rs` completely for this pass (259 lines, 8251 bytes).
