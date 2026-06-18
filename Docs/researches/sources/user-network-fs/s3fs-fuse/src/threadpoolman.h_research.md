# sources/user-network-fs/s3fs-fuse/src/threadpoolman.h

## Purpose
Declares the thread-pool manager interface and work-item contract for asynchronous S3fsCurl operations.

## Important APIs, Types, And Control Flow
`thpoolman_worker` is a function pointer taking `S3fsCurl&` and `void*`. `thpoolman_param` carries `args`, optional completion `Semaphore*`, and `pfunc`. `ThreadPoolMan` exposes singleton lifecycle (`Initialize`, `Destroy`), worker-count accessors, asynchronous `Instruct`, and synchronous `AwaitInstruct`. Private methods own worker startup/shutdown, queueing, exit flags, and the worker entry point.

## State And Persistence
The class stores singleton state, static default worker count, an instruction queue, semaphore, thread list, and futures. It is process-scoped and non-copyable/non-movable.

## Dependencies And Integration Points
Includes atomics, futures, lists, mutexes, vectors, `common.h` annotations, and `psemaphore.h`; forward-declares `S3fsCurl`. It is the public concurrency contract for parts of s3fs that need pooled curl work.

## Risks And Test Signals
Raw `void*` arguments and function pointers make type safety caller-owned. Completion semaphore lifetime must outlive execution. `SetWorkerCount` only affects future initialization. Integration and sanitizer scripts are the main signals; unit-level direct coverage is not present in this subset.
