## sources/user-network-fs/gcsfuse/internal/workerpool/static_worker_pool.go

Purpose: Fixed-size goroutine worker pool with separate priority and normal queues.

Important APIs/types/functions: `staticWorkerPool`, `NewStaticWorkerPool`, `NewStaticWorkerPoolForCurrentCPU`, `newStaticWorkerPoolForCurrentCPU`, `Start`, `Stop`, `Schedule`, and worker loop `do`.

Control flow: constructor validates nonzero workers and sizes channels by worker count capped by `2*readGlobalMaxBlocks`. CPU helper chooses `3*numCPU`, caps to `ceil(1.1*readGlobalMaxBlocks)`, reserves 10% priority workers, starts pool. Priority workers only consume priority tasks; normal workers prefer priority tasks but also consume normal tasks. `Stop` closes `stop`, waits, then closes task channels.

State and persistence behavior: maintains goroutines, channels, and wait group only in memory. Scheduled tasks execute side effects defined by `Task.Execute`.

Dependencies and integration points: implements `WorkerPool` for read/download scheduling or other background task execution. Uses internal logger and runtime CPU count.

Risks: reading from closed task channels yields nil `Task` and `task.Execute()` would panic if channels close before workers stop; current stop ordering mitigates by waiting before close. `Schedule` after stop panics. Zero `readGlobalMaxBlocks` with nonzero workers creates zero-cap channels and CPU helper can select zero total workers, causing constructor error.

Test signals: `static_worker_pool_test.go` covers constructor sizing, start/schedule/stop behavior, high task volume, post-stop panic, and CPU-based worker count.
