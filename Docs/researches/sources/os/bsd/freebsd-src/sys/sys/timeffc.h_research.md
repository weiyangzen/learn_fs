# File Research: sources/os/bsd/freebsd-src/sys/sys/timeffc.h

Feed-forward clock public and kernel interface for FreeBSD's alternate clock synchronization model.

Key responsibilities:
- Defines `struct ffclock_estimate`, the user/kernel estimate passed by synchronization daemons, including update time, counter value, next leap-second counter, period estimate, error bounds, status, total leap seconds, and pending leap adjustment.
- Under kernel BSD visibility, declares sysclock/ffclock sysctl trees, system clock selectors, feed-forward status bits, snapshot conversion flags, feedback and feed-forward clock info records, and `struct sysclock_snap`.
- Declares snapshot, conversion, reset, counter-read, last-tick, absolute-time, interval-time, and error-bound APIs for feed-forward clocks.
- Declares full wrapper families for feed-forward and feedback absolute/uptime accessors in bintime, timespec, and timeval forms.
- Provides inline `*_fromclock()` selectors that route to feedback or feed-forward implementations by `SYSCLOCK_*`.
- In userland, declares `ffclock_getcounter`, `ffclock_getestimate`, and `ffclock_setestimate`.

Dependencies:
- Includes `_ffcounter`; kernel declarations depend on `bintime`, `timespec`, `timeval`, sysctl declarations, and timecounter internals.

Notable risks:
- Flag combinations alter whether timestamps are fast, monotonic-interpolated, leap-second-adjusted, or uptime-relative.
- This header deliberately exposes specialized feedback-clock entry points but warns they are not general-consumption APIs.
