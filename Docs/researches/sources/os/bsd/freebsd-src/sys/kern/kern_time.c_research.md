# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_time.c

Read status: complete file reviewed.

This file implements FreeBSD's time-related syscall layer and timer services: clock get/set/resolution, nanosleep, gettimeofday/settimeofday, BSD interval timers, POSIX timers, CPU clocks, timer signal delivery, and timer cleanup for exec/exit.

Clock IDs are backed by `posix_clocks[MAX_CLOCKS]`; POSIX realtime timer support is registered at boot by `itimer_start`, which creates the `itimer` UMA zone, registers realtime-style handlers for CLOCK_REALTIME/MONOTONIC/UPTIME/TAI, and fills POSIX.1B sysctl capability values.

Clock read paths include `sys_clock_gettime`, `kern_clock_gettime`, `kern_clock_getcpuclockid2`, CPU-clock helpers, and `kern_clock_getres`. Realtime, monotonic, uptime, fast, precise, second, TAI, virtual/profiling, process CPU, thread CPU, and encoded per-process/per-thread CPU clock IDs are supported. CPU clocks derive from thread/process runtime and `cpu_tickrate`.

Clock set paths include `sys_clock_settime`, `kern_clock_settime`, `sys_settimeofday`, `kern_settimeofday`, and internal `settime`. They enforce `PRIV_CLOCK_SETTIME`/`PRIV_SETTIMEOFDAY`, validate ranges, optionally reject extreme dates, clamp steps under securelevel, call `tc_setclock`, and reset the time-of-day hardware via `resettodr`.

Sleep paths include `kern_nanosleep`, `kern_clock_nanosleep`, `sys_nanosleep`, and `sys_clock_nanosleep`. They validate clock/flags, support absolute and relative sleeps, choose precise or coarse sbintime deadlines, handle realtime jumps with `td_rtcgen`, chunk very large sleeps, return remaining time for interrupted relative sleeps, and map POSIX errors through `kern_posix_error`.

Legacy interval timers are handled by `kern_getitimer`, `kern_setitimer`, `realitexpire`, `itimerfix`, `itimerdecr`, and timeval helpers. `ITIMER_REAL` is stored as an absolute uptime deadline and scheduled with a callout; virtual/profiling timers live in `p_stats` and are decremented elsewhere. Periodic realtime expiry advances by intervals until future time to avoid drift and compresses missed signals into one SIGALRM.

Rate helpers `ratecheck` and `eventratecheck` provide timeval/tick based rate limiting. Basic `timevaladd`, `timevalsub`, and `timevalfix` normalize timeval arithmetic.

POSIX timer creation/deletion/set/get paths include `sys_ktimer_create`, `kern_ktimer_create`, `kern_ktimer_delete`, `kern_ktimer_settime`, `kern_ktimer_gettime`, `kern_ktimer_getoverrun`, and `itimer_find`. Timers validate sigevent modes/signals, allocate per-process timer arrays lazily, reserve IDs 0-2 for setitimer compatibility, store ksiginfo, protect timers with `it_mtx`, use `ITF_DELETING/ITF_WANTED` and usecounts to serialize deletion, and remove pending queued signals on delete.

Realtime POSIX timer backend functions (`realtimer_create`, `realtimer_delete`, `realtimer_gettime`, `realtimer_settime`, `realtimer_expire_l`) manage callouts, absolute deadlines, relative/absolute settime conversion, interval overrun accounting, stopped/killed process deferral with `ITF_PSTOPPED`, and rescheduling based on clock time.

`itimer_fire` delivers SIGEV_SIGNAL or SIGEV_THREAD_ID notifications through `tdsendsignal`, updates overrun counters if a previous signal is still queued, disables timers whose target thread cannot be found, and records ERANGE on overrun saturation. `itimer_accept` transfers overrun state when a queued timer signal is accepted.

Process lifecycle hooks `itimers_exec` and `itimers_exit` delete POSIX timers on exec/exit, preserving XSI interval timers across exec as required. `itimer_proc_continue` restarts deferred legacy and POSIX realtime timers when a stopped process resumes.

Risk areas are realtime clock jumps versus absolute sleeps/timers, deletion races with active callouts and signal delivery, timer overrun saturation, proc lock versus timer lock ordering, preserving setitimer timer IDs while sharing POSIX cleanup code, CPU-clock lookup lifetime, and stopped/killed process timer deferral/restart semantics.
