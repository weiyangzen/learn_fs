# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_sched.c

This file implements the `ksched` backend used by POSIX.1b priority scheduling glue. It maps POSIX scheduling policies and priorities onto DragonFlyBSD realtime priority (`rtprio`) fields.

Core behavior:
- `ksched_attach()` allocates `struct ksched` and initializes the round-robin interval to 100 ms.
- `ksched_detach()` frees it.
- `getscheduler()` maps `RTP_PRIO_FIFO` to `SCHED_FIFO`, `RTP_PRIO_REALTIME` to `SCHED_RR`, and other types to `SCHED_OTHER`.
- `ksched_setparam()` rejects parameter-only changes for `SCHED_OTHER` and otherwise delegates to `ksched_setscheduler()`.
- `ksched_getparam()` returns POSIX priority for realtime classes.
- `ksched_setscheduler()` validates POSIX priority range, translates priority numbering, sets `lwp_rtprio`, and calls `need_user_resched()`.
- `ksched_yield()` delegates to the process scheduler's `yield()` operation for the current LWP.
- `ksched_get_priority_max()` and `ksched_get_priority_min()` report policy ranges.
- `ksched_rr_get_interval()` returns the configured RR interval.

Filesystem/storage relevance:
- Not filesystem code, but it can influence scheduling of filesystem userland daemons, realtime workloads, and kernel-adjacent services.
