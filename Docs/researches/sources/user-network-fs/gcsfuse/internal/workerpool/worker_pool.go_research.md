## sources/user-network-fs/gcsfuse/internal/workerpool/worker_pool.go

Purpose: Defines worker pool abstraction used by concrete schedulers.

Important APIs/types/functions: `Task` interface with `Execute()` and `WorkerPool` interface with `Start`, `Stop`, and `Schedule(urgent bool, task Task)`.

Control flow: interface-only file; concrete implementations decide scheduling and lifecycle semantics.

State and persistence behavior: none.

Dependencies and integration points: allows consumers to depend on a small interface rather than `staticWorkerPool`.

Risks: interface does not specify error handling, post-stop behavior, backpressure, or whether `Stop` drains queued tasks.

Test signals: concrete behavior is tested in `static_worker_pool_test.go`.
