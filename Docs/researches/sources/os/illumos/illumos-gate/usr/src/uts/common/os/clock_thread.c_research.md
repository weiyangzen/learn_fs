# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_thread.c

This file registers read-only thread CPU-time clock backends for `CLOCK_VIRTUAL` and `CLOCK_THREAD_CPUTIME_ID`.

Core behavior:
- `CLOCK_VIRTUAL` reports only the current thread’s `LMS_USER` microstate time from `lwp_mstate.ms_acct[LMS_USER]`, scaled with `scalehrtime()`.
- `CLOCK_THREAD_CPUTIME_ID` reports current thread user plus system plus trap time through `mstate_thread_onproc_time()`, under `thread_lock()`.
- `clock_thread_getres()` reports `cyclic_getres()` as the closest practical resolution for this subsystem.
- `clock_thread_settime()` and all timer operations return `EINVAL`; interval timers are not implemented.
- `clock_thread_init()` registers two backend structures: one for `CLOCK_VIRTUAL`, one for `CLOCK_THREAD_CPUTIME_ID`.

Important invariants:
- Both clocks always refer to the calling thread, so no cross-process privilege or lifetime lookup is needed.
- `mstate_thread_onproc_time()` is used for the user+system clock because it includes currently executing system time not yet folded into stored microstate counters.
- Timer metadata is initialized but timer support is intentionally absent.
