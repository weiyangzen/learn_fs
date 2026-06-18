# sources/user-network-fs/s3fs-fuse/src/threadpoolman.cpp

## Purpose
Implements the singleton `ThreadPoolMan` used to run S3fsCurl-backed worker functions on a fixed pool of threads. It centralizes parallel request execution and per-thread curl/share cleanup.

## Important APIs, Types, And Control Flow
`Initialize` creates the singleton, optionally updates `worker_count`, and starts workers. `Destroy` resets it. `SetWorkerCount` validates positive counts but does not resize a live pool. `Instruct` requires a non-null completion semaphore and enqueues work. `AwaitInstruct` wraps a work item in a local semaphore and blocks until completion. `Worker` creates one `S3fsCurl` object per thread, waits on `thpoolman_sem`, recreates the curl handle for each instruction, pops a `thpoolman_param`, runs `pfunc`, releases the instruction semaphore, and destroys thread-local curl share state on exit. `StopThreads` sets `is_exit`, releases workers, joins them, reads futures, clears lists, and drains the semaphore.

## State And Persistence
Global state is the singleton and static `worker_count`. Instance state includes an atomic exit flag, semaphore, vector of `(thread, future)`, and instruction list guarded by a mutex. There is no disk persistence, but worker functions can perform S3/cache mutations through their arguments.

## Dependencies And Integration Points
Depends on `threadpoolman.h`, `s3fs_logger.h`, `curl.h`, `curl_share.h`, std threads/futures, and `Semaphore`. It integrates with multipart uploads/downloads, parallel copy, and any code that submits `thpoolman_param` work.

## Risks And Test Signals
No explicit null check for `param.pfunc` exists before worker invocation. The queue can retain unprocessed instructions if `CreateCurlHandle` fails and breaks a worker. `StopThreads` holds `thread_list_lock` while joining, which is acceptable only because workers do not need that lock after exit is signaled. `reinterpret_cast<long>` of an `int` future value is suspicious in logging. Signals come from integration tests for multipart upload/copy/mix, concurrent reads/writes, skipped writes, and sanitizer runs, especially ThreadSanitizer.
