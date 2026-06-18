# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_synch.c

Purpose: Implements kernel sleep/wakeup queues, sleeps with mutex/rwlock release, thread sleep/wakeup syscalls, reference counts, and simple condition waits.

Sleep/wakeup:
- `sleep_queue_init()` initializes hashed sleep queues by wait-channel address.
- `tsleep_nsec()` and `tsleep()` sleep on a channel, with signal and timeout semantics.
- `msleep_nsec()` and `msleep()` sleep while atomically releasing and optionally reacquiring a mutex.
- `rwsleep_nsec()` and `rwsleep()` do the same for rwlocks, restoring prior read/write status.
- `sleep_setup()` places the current thread on the hashed sleep queue and marks state.
- `sleep_finish()` arms/cancels timeouts, handles signal checks, suspension, scheduler switching, and timeout races.
- `wakeup_proc()`, `endtsleep()`, `unsleep()`, `wakeup_n()`, and `wakeup()` remove sleepers and make them runnable.

Signal and scheduler integration:
- `sleep_signal_check()` integrates interruptible sleeps with process suspension, stop signals, `cursig()`, `EINTR`, and `ERESTART`.
- `sys_sched_yield()` requeues the current thread and switches, using sibling run priorities for multithreaded processes.

User thread sleeps:
- `tslp_init()` initializes bucketed userspace thread-sleep queues.
- `sys___thrsleep()` copies and validates absolute timeout input, unlocks a userspace atomic lock, optionally checks abort, and sleeps on a stack entry.
- `sys___thrwakeup()` wakes matching waiters in the same process, or all shared `ident == -1` waiters.
- Bucket locks interlock userspace wakeups against sleep insertion/removal.

Reference and condition helpers:
- `refcnt_init()`, `refcnt_take()`, `refcnt_rele()`, `refcnt_rele_wake()`, `refcnt_finalize()`, and `refcnt_read()` provide traced atomic reference counting with memory barriers.
- `cond_init()`, `cond_signal_handler()`, and `cond_wait()` implement a small wait/signal primitive used by SMR and scheduler barriers.

Filesystem relevance:
- This file supplies the blocking, wakeup, timeout, and refcount mechanics used by VFS, buffer cache, locks, vnode teardown, and file/device wait paths.
