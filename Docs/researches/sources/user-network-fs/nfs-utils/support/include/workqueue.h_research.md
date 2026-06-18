# sources/user-network-fs/nfs-utils/support/include/workqueue.h

## Purpose
Declares a tiny synchronous worker queue abstraction used to run operations in a configured chroot.

## Important APIs, Types, and Functions
`struct xthread_workqueue`, `xthread_workqueue_alloc()`, `xthread_workqueue_shutdown()`, `xthread_work_run_sync()`, and `xthread_workqueue_chroot()`.

## Control Flow
Callers allocate a worker, optionally ask it to chroot, run function/data jobs synchronously, and shut it down.

## State and Persistence Behavior
Implementation owns worker thread state and queue synchronization. Chroot changes affect the worker thread environment.

## Dependencies and Integration Points
Used by `nfsd_path.c` to run filesystem calls under `exports.rootdir`.

## Risks and Edge Cases
Threading availability and chroot failure behavior are implementation-sensitive. Synchronous calls can deadlock if invoked reentrantly from the worker.

## Test Signals
Test allocation/shutdown, synchronous execution ordering, chroot setup, failure paths, and no-thread fallback builds.
