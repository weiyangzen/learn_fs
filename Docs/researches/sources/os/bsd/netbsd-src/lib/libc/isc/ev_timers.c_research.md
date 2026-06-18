# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/ev_timers.c

Read completely: 519 lines.

This file implements eventlib time helpers and, outside `_LIBC`, timer management for ISC eventlib. The always-built helpers construct, add, subtract, compare, and convert `timespec`/`timeval` values, and obtain current time using `clock_gettime` with optional monotonic time support or `gettimeofday` fallback.

The non-libc timer implementation stores `evTimer` objects in a heap ordered by due time. Public operations create, clear, reconfigure, reset, and touch ordinary or idle timers. Idle timers wrap user callbacks in an `idle_timer` object that tracks last activity and reschedules or fires based on `ctx->lastEventTime`.

Important interactions: depends on `eventlib_p.h` for `evContext_p`, allocation macros, timer structures, heap wrappers, debug printing, and `__evOptMonoTime`. Timer deletion while currently executing is deferred by setting interval to zero so event dispatch cleanup can safely drop it.

Security/reliability notes: input validation rejects negative or out-of-range nanoseconds, except HP-UX compatibility assumes unsigned fields. Timer IDs are raw internal pointers; stale or forged IDs are checked only by comparing heap slots against the pointer. Idle timer cleanup is delicate because it frees wrapper state and mutates interval from callback paths.
