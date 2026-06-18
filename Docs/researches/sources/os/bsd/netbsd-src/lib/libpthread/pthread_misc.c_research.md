# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_misc.c

This file implements miscellaneous pthread operations for scheduling, affinity, signals, and thread-directed signals. `pthread_getschedparam`, `pthread_setschedparam`, `pthread_getaffinity_np`, `pthread_setaffinity_np`, `pthread_setschedprio`, and `pthread_kill` all validate thread magic, check that the thread is still findable with `pthread__find`, then call NetBSD LWP or scheduler syscalls using the thread's LWP id.

`pthread_sigmask` wraps `__sigprocmask14` and returns errno-style errors. `pthread__sched_yield` dispatches either to the libc stub or `_sys_sched_yield`.

Integration points: uses scheduler compatibility functions from `pthread_compat.c`, libc strong aliases for `pthread_sigmask` and yield, and private thread lookup state. Risks include races with thread termination, scheduler-policy differences from POSIX expectations, and preserving errno-return conventions.
