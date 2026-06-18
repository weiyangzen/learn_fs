## sources/user-network-fs/gcsfuse/internal/workerpool/static_worker_pool_test.go

Purpose: Tests static worker pool construction, scheduling, execution, stop behavior, and CPU-based sizing.

Important APIs/types/functions: `dummyTask`, `TestNewStaticWorkerPool_Success/Failure`, `TestStaticWorkerPool_Start`, priority/normal scheduling tests, high task count, schedule-after-stop panic, stop channel closure assertions, and CPU helper tests.

Control flow: tests create pools, start them when needed, schedule dummy tasks, and use `assert.Eventually` to wait for execution or queue drain. Sizing tests assert channel capacities and worker counts.

State and persistence behavior: starts goroutines and closes them with `Stop`; no external state.

Dependencies and integration points: validates workerpool contract and runtime CPU helper. Uses testify assertions and timing loops.

Risks: `dummyTask.executed` is a plain bool written/read across goroutines, so tests have a data race under `-race`. Queue-empty assertions do not prove all tasks finished because a worker may have dequeued but not completed a task.

Test signals: broad functional coverage, with concurrency-race caveat.
