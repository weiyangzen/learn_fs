# File Research: sources/os/bsd/dragonflybsd/sys/sys/_timespec.h

Read completely: 47 lines.

This header defines `struct timespec`.

Key contents:
- Declares `time_t` if needed.
- Defines seconds plus nanoseconds fields: `tv_sec` and `tv_nsec`.

Security/reliability notes:
- No runtime logic. Layout is ABI-sensitive for POSIX time, clocks, timers, nanosleep, and stat timestamps.
