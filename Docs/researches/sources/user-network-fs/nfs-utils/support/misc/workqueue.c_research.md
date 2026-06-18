# sources/user-network-fs/nfs-utils/support/misc/workqueue.c

Purpose: small synchronous workqueue abstraction used to run operations, especially `chroot()`, in a helper thread with a private filesystem namespace when platform support exists.

Important APIs and types: `struct xthread_workqueue` owns a FIFO queue, mutex, and condition variable. `xthread_workqueue_alloc()`, `xthread_workqueue_shutdown()`, `xthread_work_run_sync()`, and `xthread_workqueue_chroot()` are the public-facing operations. The fallback build uses a dummy singleton and runs work inline.

Control flow: when `HAVE_SCHED_H`, `HAVE_LIBPTHREAD`, and `HAVE_UNSHARE` are available, allocation creates a worker thread and waits until it signals startup. `xthread_work_run_sync()` pushes a stack-allocated work item, signals the worker, and waits on the item condition until the function finishes. `xthread_workqueue_chroot()` runs `unshare(CLONE_FS)` and `chroot(path)` on the worker.

State and persistence: state is process-local queue/thread state. No durable persistence. Shutdown sets a flag and wakes the worker; cleanup frees the queue via pthread cleanup handler.

Dependencies and integration: depends on pthreads, `unshare()`, `chroot()`, `xlog`, and `workqueue.h`. It lets code isolate filesystem-root changes away from the main thread when supported.

Risks: work functions run while the queue mutex remains locked, so nested queue calls or long-running work block all queue activity. The worker thread is not detached or joined visibly here, so lifetime ownership must be clear at call sites. The fallback silently runs work inline except for `chroot`, which only logs an error, so behavior differs substantially by build configuration.

Test signals: verify synchronous completion ordering, shutdown wakeup, chroot success/failure logging, fallback behavior, and deadlock risk if a work function reenters the queue.
