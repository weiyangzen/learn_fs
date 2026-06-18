# File Research: sources/os/bsd/freebsd-src/sys/sys/time.h

Core FreeBSD time ABI and kernel timekeeping interface header.

Key responsibilities:
- Defines `struct timezone`, DST constants, interval timer IDs, `struct itimerval`, `struct clockinfo`, and CPU clock selector constants.
- Under BSD visibility, defines `struct bintime`, fixed-point `sbintime_t` constants, bintime arithmetic helpers, sbintime/bintime/timespec/timeval conversions, and scaling helpers with explicit floor/ceil rounding.
- Provides timespec/timeval/timer macros for clear, isset, compare, add, subtract, and valid interval checks.
- Under `_KERNEL` or `_STANDALONE`, declares clock driver hooks, exported timecounter state, UTC/uptime timestamp accessors, boottime accessors, itimer/rate/tvtohz helpers, tick conversion macros, and frequency conversion macros.
- For userland, declares `setitimer`, `utimes`, and BSD/XSI time APIs including `adjtime`, `gettimeofday`, `settimeofday`, and `clock_getcpuclockid2`.

Dependencies:
- Includes `_timeval`, `types`, `timespec`, and `_clock_id`; kernel consumers depend on global `hz`, timecounter state, and `struct bintime`.

Notable risks:
- This is a high-visibility ABI and kernel timing contract; layout, rounding behavior, and macro semantics affect libc, drivers, timers, schedulers, and filesystem timestamp code.
- The conversion helpers intentionally use floor/ceil asymmetrically; replacing them with ordinary rounding would change interval and timeout guarantees.
