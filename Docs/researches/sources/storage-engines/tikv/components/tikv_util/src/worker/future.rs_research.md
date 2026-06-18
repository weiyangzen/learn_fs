# sources/storage-engines/tikv/components/tikv_util/src/worker/future.rs

Purpose: single-threaded future-aware worker abstraction backed by an unbounded futures mpsc channel and a current-thread Tokio runtime.

Important APIs/types/functions: `Runnable<T>`, `Scheduler<T>`, `Worker<T>`, `Stopped<T>`, `dummy_scheduler`, and internal `poll`.

Control flow: `Scheduler::schedule` sends `Some(task)` and increments pending metrics. The worker thread receives messages, runs `runner.run`, decrements pending, increments handled, and breaks on `None`; after the loop it calls `runner.shutdown`.

State and persistence: in-memory channel, worker join handle, metrics gauges/counters, and optional receiver protected by a `Mutex` to prevent double start.

Dependencies/integration: integrates with `tokio::task::LocalSet`, legacy `tokio_timer` futures, Prometheus worker metrics, and thread-group propagation.

Risks: scheduling increments metrics after successful send but `run` panics can skip decrements; `is_busy` really means not currently startable/handle missing, not queue saturation.

Test signals: tests cover asynchronous timer tasks executing concurrently and nested `block_on` inside the worker.
