# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_time.c

Implements kernel time-of-day syscalls, POSIX clock operations, nanosleep, interval timers, NTP adjustment controls, timeval helpers, and rate-limit helpers.

Key areas:
- Clock get/set/resolution: `kern_clock_gettime()`, `sys_clock_gettime()`, `kern_clock_settime()`, `sys_clock_settime()`, `kern_clock_getres()`.
- CPU clock IDs: `kern_getcpuclockid()`, `sys_getcpuclockid()`.
- Sleep: `clock_nanosleep1()`, `nanosleep1()`, `sys_clock_nanosleep()`, `sys_nanosleep()`.
- Time of day: `sys_gettimeofday()`, `sys_settimeofday()`, `settime()`.
- NTP adjustment: `kern_adjtime()`, `kern_reladjtime()`, `kern_adjfreq()`, `sys_adjtime()`, `sysctl_adjtime()`, `sysctl_delta()`, `sysctl_adjfreq()`.
- Interval timers: `sys_getitimer()`, `sys_setitimer()`, `realitexpire()`.
- Helpers: `itimerfix()`, `itimespecfix()`, `itimerdecr()`, `timevaladd()`, `timevalsub()`, `ratecheck()`, `ppsratecheck()`.

Important behavior:
- `settime()` moves execution to CPU 0 if necessary, computes delta, enforces securelevel clamping, calls `set_timeofday()`, then updates the RTC via `resettodr()`.
- `kern_clock_gettime()` supports realtime, monotonic, uptime, fast/precise variants, process CPU time, thread CPU time, and encoded process/LWP CPU clocks.
- `clock_nanosleep1()` combines coarse `tsleep()` with fine-grained one-shot `systimer` sleeps, and may yield or spin for very small intervals controlled by `kern.nanosleep_min_us` and `kern.nanosleep_hard_us`.
- `sys_gettimeofday()` optionally uses coarse `getmicrotime()` when `kern.gettimeofday_quick` is enabled; the sysctl also updates `kpmap->fast_gtod`.
- `sys_setitimer()` stores real timers as absolute uptime and schedules `p_ithandle` callouts; virtual/profiling timers live in process timer arrays.
- `realitexpire()` sends `SIGALRM` and advances periodic real timers without drift, compressing delayed expirations into one signal.
- NTP sysctls expose permanent frequency correction, one-time delta, tick delta state, leap second state, and relative adjustment.

Concurrency and privilege:
- Time setting requires `SYSCAP_NOSETTIME` privilege checks and uses `masterclock_lock`.
- NTP state is protected by `ntp_spin`.
- Process and LWP timing uses process tokens and reference holds.

Filesystem relevance:
- Provides timestamp validation helpers used by time-setting syscalls and filesystem metadata update paths.
- VFS/file code can depend on `itimerfix()`, `itimespecfix()`, realtime/uptime clocks, and rate limiting helpers for event throttling and timestamp correctness.
