# File Research: sources/os/bsd/freebsd-src/sys/sys/timespec.h

Timespec utility and POSIX interval timer specification header.

Key responsibilities:
- Includes the canonical `struct timespec` definition.
- Under BSD visibility, defines `TIMEVAL_TO_TIMESPEC` and `TIMESPEC_TO_TIMEVAL` conversion macros.
- Defines `struct itimerspec` with interval and current-value `timespec` fields for POSIX timer syscalls.

Dependencies:
- Includes `sys/cdefs.h` and `sys/_timespec.h`.

Notable risks:
- The timeval conversion macros truncate nanoseconds to microseconds when converting back to timeval.
- `struct itimerspec` is a public ABI shared by POSIX timers and timerfd.
