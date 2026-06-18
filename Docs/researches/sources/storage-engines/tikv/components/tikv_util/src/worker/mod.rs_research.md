# sources/storage-engines/tikv/components/tikv_util/src/worker/mod.rs

Purpose: public module facade for TiKV background worker abstractions.

Important APIs/types/functions: re-exports classic pool workers (`Builder`, `Worker`, `Scheduler`, `Runnable`, `RunnableWithTimer`, `LazyWorker`) and future workers (`FutureWorker`, `FutureScheduler`, `FutureRunnable`, `Stopped`).

Control flow: this file mostly delegates to submodules. Its local tests exercise scheduling, threaded producers, worker shutdown, and pending capacity through the exported API surface.

State and persistence: no state in the module facade.

Dependencies/integration: gives downstream TiKV components a stable import path for worker APIs and hides submodule layout.

Risks: exported names overlap between classic and future workers, so aliases matter for callers; tests use sleeps around busy-state updates.

Test signals: module tests cover sequential handling, cross-thread scheduling, shutdown callbacks, and capacity errors.
