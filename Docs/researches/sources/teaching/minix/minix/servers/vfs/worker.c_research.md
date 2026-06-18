# File Research: sources/teaching/minix/minix/servers/vfs/worker.c

## Purpose
Implements the VFS worker thread pool, request assignment, pending work handling, thread sleep/wake operations, blocked-send interruption, and special process-context switching for reboot.

## Main Entry Points
- `worker_init()` creates worker threads and synchronization state.
- `worker_cleanup()` shuts workers down for live update.
- `worker_idle()` reports whether no work is pending or busy.
- `worker_allow()` gates processing of new work during initialization.
- `worker_available()` reports free workers, including the spare.
- `worker_can_start()` checks whether normal work can be scheduled for a process.
- `worker_start()` schedules normal or postponed PM work.
- `worker_yield()` yields to workers from the main thread.
- `worker_wait()` and `worker_signal()` provide worker sleep/wake used by TLL.
- `worker_stop()` and `worker_stop_by_endpt()` interrupt blocked FS/driver communication.
- `worker_get()` finds a worker by thread ID.
- `worker_set_proc()` changes current worker process context for reboot-only code.

## Scheduling Model
Each `struct fproc` may have at most one normal job and one postponed PM job. `worker_start()` stores the message and function pointer or PM message, then activates a worker when available. If none can run, the process is marked `FP_PENDING`, and the global `pending` count is incremented.

The pool keeps one spare worker by default for deadlock resolution. Normal work requires at least two available workers unless `use_spare` is true. Callback-style work may use the spare.

## Worker Loop
`worker_main()` binds `self`, repeatedly obtains work, sets global `fp`, locks the process, executes normal work if present, executes postponed PM work if present, runs `thread_cleanup()`, unlocks the process, clears worker ownership, and decrements `busy`.

## Initialization and Cleanup
`worker_init()` configures stack size based on build mode, initializes events, creates `NR_WTHREADS`, and yields to let them sleep. `worker_cleanup()` requires all workers idle, wakes each with no assigned process to terminate, joins them, destroys synchronization objects, and zeroes the worker table.

## Blocking and Wakeup
`worker_sleep()` waits on the worker condition variable and restores `self`. `worker_suspend()` saves error state before a thread blocks; `worker_resume()` restores globals after wake. TLL locks use `worker_wait()`/`worker_signal()`.

## Failure Handling
`worker_stop()` turns blocked FS/driver sendrec storage into `EIO`, clears the blocked pointer, and wakes the worker. `worker_stop_by_endpt()` applies this to workers blocked on a dead endpoint.

## Risks and Notes
The global counters `pending` and `busy` are consistency-critical. `worker_start()` contains multiple panic checks for duplicate jobs or impossible pending/active combinations. `worker_set_proc()` explicitly violates normal threading rules and is restricted to reboot handling.
