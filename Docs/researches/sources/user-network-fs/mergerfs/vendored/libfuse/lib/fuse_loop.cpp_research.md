# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_loop.cpp

## Purpose
`fuse_loop.cpp` implements the multi-threaded FUSE read/process loop used by mergerfs. It separates request reads from optional request processing workers, supports cloned `/dev/fuse` fds, applies CPU pinning policies, and starts/stops maintenance jobs around the loop.

## Important APIs, Types, and Functions
`fuse_session_loop_mt` is the main loop. `fuse_loop_mt` wraps it for `struct fuse` using `fuse_cfg`. `AsyncWorker` reads requests and enqueues processing lambdas to a process thread pool. `SyncWorker` reads and processes inline. `_calculate_thread_counts` interprets raw configuration values, and `_retriable_receive_error` masks transient receive errors.

## Control Flow
The loop computes read/process counts, optionally creates a processing `ThreadPool`, asks the session to clone fds for read threads, starts read workers, captures pthread ids, pins them, logs the effective configuration, then waits on a semaphore until a worker exits and marks the session exited. On shutdown it cancels read threads and destroys thread pools. `fuse_loop_mt` surrounds this with `MaintenanceThread::setup`, `fuse_populate_maintenance_thread`, and `MaintenanceThread::stop`.

## State and Persistence
Loop state is transient: thread pools, semaphores, msgbuf allocations, and session exit status. Message buffers are allocated per received request and freed after processing. The maintenance thread is process-local and periodic.

## Dependencies and Integration Points
It depends on `thread_pool.hpp`, `pin_threads`, `maintenance_thread`, `fuse_i`, `fuse_lowlevel`, `fuse_msgbuf`, `fuse_cfg`, `fmt`, syslog, pthread cancellation, and POSIX semaphores. It calls session receive/process callbacks installed by `fuse_lowlevel.cpp`.

## Risks
Thread-count calculation must avoid zero or negative queue depths. Async mode requires every enqueued closure to free its msgbuf exactly once. Cancellation is enabled only during blocking reads; changing that can introduce leaks or inconsistent callback execution. A read worker exiting for one fatal fd error exits the whole session.

## Test Signals
Exercise configured thread counts `0`, negative divisors, positive values, process-thread disabled mode, process-thread enabled mode, cloned fd success and fallback, EINTR/EAGAIN/ENOENT receive retry, ENODEV shutdown, and pinning strings from `pin_threads.cpp`.
