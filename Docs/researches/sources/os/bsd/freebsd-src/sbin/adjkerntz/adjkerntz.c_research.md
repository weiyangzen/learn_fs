# File Research: sources/os/bsd/freebsd-src/sbin/adjkerntz/adjkerntz.c

## Purpose
Adjusts kernel time and timezone state when the machine uses a local-time CMOS clock, indicated by `/etc/wall_cmos_clock`. It handles boot-time initialization and later adjustment calls across timezone/DST changes.

## Main Elements
- `main()`: parses `-i`, `-a`, and `-s`; checks wall-clock marker; daemonizes for initial mode; loops on signal-triggered adjustment.
- Uses `sysctlbyname()` for `machdep.adjkerntz`, `machdep.disable_rtc_set`, and `machdep.wall_cmos_clock`.
- Computes local-to-GMT offset using `localtime()`, `mktime()`, `tm_gmtoff`, current kernel offset, and `gettimeofday()` timezone fields.
- Handles DST edge cases by recalculating final offset and retrying nonexistent local times in sleep mode.
- Uses `settimeofday()` to clear obsolete timezone state and adjust wall-clock-derived kernel time.
- Temporarily disables RTC writes while changing kernel time/offset in paths where RTC should not be rewritten.
- `fake()` is a no-op signal handler used with `sigsuspend()`.
- `usage()` prints init/adjustment invocation forms and exits.

## Dependencies And Integration
Run from rc/periodic system paths. Depends on kernel machine-dependent time sysctls, `/etc/wall_cmos_clock`, libc timezone rules, syslog, and process signals.

## Behavioral Notes
The program has a timing-sensitive critical section around reading time, computing offset, setting system time, updating kernel offset, and restoring RTC-write behavior. In initial mode it can daemonize and wait for `SIGTERM`-driven adjustment cycles.

## Risk Notes
This utility changes system time and kernel RTC behavior. Failures after disabling RTC writes but before restoration are explicitly called out as risky in comments.
