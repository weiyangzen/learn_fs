# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_compat.c

This compatibility file supplies libc symbols not present before NetBSD 5.0 and initializes libc threading/atomic support from a constructor. `__pthread_init` calls `__libc_atomic_init` and `__libc_thr_init` before normal program execution.

The rest of the file provides direct syscall-backed implementations for LWP, scheduler, aio, and message queue helper symbols such as `_lwp_kill`, `_lwp_detach`, `_lwp_park`, `_lwp_unpark`, `_lwp_unpark_all`, `_lwp_setname`, `_lwp_getname`, `_lwp_ctl`, `_sched_setaffinity`, `_sched_getaffinity`, `_sched_setparam`, `_sched_getparam`, `_sys_sched_yield`, `_sys_aio_suspend`, and `_sys_mq_*`. `sched_yield` is also implemented as a direct syscall.

Integration points: bridges newer libpthread code to older libc/kernel symbol availability and is used by synchronization, scheduling, cancellation, and affinity code. Risks are compatibility-only path rot and syscall-number or prototype mismatches across NetBSD versions.
