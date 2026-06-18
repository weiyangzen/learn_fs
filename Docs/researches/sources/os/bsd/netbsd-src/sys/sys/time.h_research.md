# File Research: sources/os/bsd/netbsd-src/sys/sys/time.h

Read completely: 355 lines.

Defines public time structures, time conversion helpers, interval timers, and clock constants.

Key elements:
- Defines `struct timeval` and includes `struct timespec` from `sys/timespec.h`.
- NetBSD extensions provide timeval/timespec conversion and arithmetic macros.
- Defines obsolete `struct timezone` for compatibility.
- Defines `struct bintime`, bintime add/sub/compare helpers, and conversions among bintime, timeval, timespec, milliseconds, microseconds, and nanoseconds.
- Defines `itimerval`, `itimerspec`, `ITIMER_*`, `CLOCK_*`, `TIMER_ABSTIME`, and NetBSD `TIMER_RELTIME`.
- Kernel inclusion pulls in `timearith.h` and `timevar.h`.
- Userland declarations include `getitimer`, `gettimeofday`, `setitimer`, `utimes`, `adjtime`, `futimes`, `lutimes`, and `settimeofday` with time64 symbol renames where applicable.

Risks and notes:
- Public structures and constants are ABI-stable.
- Time conversion macros round down by design; callers should not expect nearest rounding.
- Kernel and userland visibility diverge substantially.
