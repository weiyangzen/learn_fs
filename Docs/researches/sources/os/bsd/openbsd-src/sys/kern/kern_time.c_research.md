# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_time.c

Read completely: 1038 lines.

Implements public time syscalls, realtime clock setting policy, nanosleep, `gettimeofday`/`settimeofday`, `adjtime`/`adjfreq`, BSD interval timers, rate limiting helpers, RTC initialization/update, and periodic RTC resynchronization.

Time syscalls:
- `settime()` validates against near-wrap future times and securelevel clock rollback restrictions, calls `tc_setrealtimeclock()`, and writes the RTC through `resettodr()`.
- `clock_gettime()` supports realtime, uptime/runtime, monotonic/boottime, process CPU time, current thread CPU time, and encoded thread CPU clocks from `pthread_getcpuclockid()`.
- `sys_clock_gettime()` copies out a `timespec` and emits ktrace structure records.
- `sys_clock_settime()` allows root to set only `CLOCK_REALTIME` after validating the requested `timespec`.
- `sys_clock_getres()` derives hardware clock resolution from timecounter frequency/precision and CPU clock resolution from `stathz`.
- `sys_nanosleep()` sleeps in bounded chunks against uptime, recomputes elapsed time after wakeups, converts restart to interrupt, and optionally copies out the remainder.
- `sys_gettimeofday()` and `sys_settimeofday()` provide legacy timeval/timezone interfaces; timezone input is validated but not used to alter kernel timezone state here.

Clock adjustment:
- `sys_adjfreq()` optionally requires root, validates the fixed-point frequency adjustment range, uses `tc_lock` read/write mode, and delegates to `tc_adjfreq()`.
- `sys_adjtime()` applies `pledge_adjtime()`, requires root for new deltas, validates timeval arithmetic against `int64_t` overflow, reports old remaining delta, and delegates to `tc_adjtime()`.

Interval timers:
- `setitimer()` gets or sets `ITIMER_REAL`, `ITIMER_VIRTUAL`, and `ITIMER_PROF`. Real timers are stored as absolute uptime deadlines and use `ps_realit_to`; virtual/prof timers are stored as remaining intervals under `itimer_mtx`.
- `cancel_all_itimers()` clears all per-process interval timers.
- `sys_getitimer()` and `sys_setitimer()` implement the system calls with validation, ktrace, and optional old-value return.
- `realitexpire()` sends `SIGALRM`, clears one-shot timers, and advances periodic real timers to the next future absolute deadline to avoid drift.
- `itimerfix()` validates user `itimerval` input, bounds it below the historical maximum, clears intervals for disabled timers, and rounds small nonzero intervals up to at least one tick.
- `itimerdecr()` decrements virtual/profiling timers and reloads periodic timers while preserving overrun.
- `itimer_update()` runs from hardclock context, decrements virtual/prof timers based on elapsed hardclock periods, and marks `P_ALRMPEND`/`P_PROFPEND`.
- `process_reset_itimer_flag()` maintains `PS_ITIMER` based on whether virtual/prof timers are active.

Rate limiting:
- `ratecheck()` implements timeval-based minimum interval checks under `ratecheck_mtx`.
- `ppsratecheck()` implements per-second event limiting, including unlimited negative `maxpps`, disabled zero `maxpps`, and wrap-safe packet count increments.

RTC and periodic sync:
- `inittodr()` initializes system time from filesystem base time and the best attached TODR chip, warns on implausible filesystem or chip time, and calls `tc_setclock()`.
- `resettodr()` writes current realtime to the TODR chip only after `inittodr()` has run.
- `todr_attach()` selects the highest-quality TODR provider.
- `periodic_resettodr()`, `perform_resettodr()`, `start_periodic_resettodr()`, and `stop_periodic_resettodr()` use `systq` plus a timeout to periodically update the RTC every 1800 seconds.
