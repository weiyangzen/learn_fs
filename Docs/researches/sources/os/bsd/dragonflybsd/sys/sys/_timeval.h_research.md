# File Research: sources/os/bsd/dragonflybsd/sys/sys/_timeval.h

Read completely: 55 lines.

This header defines `struct timeval`.

Key contents:
- Declares `suseconds_t` and `time_t` if needed.
- Defines seconds plus microseconds fields: `tv_sec` and `tv_usec`.

Security/reliability notes:
- No runtime logic. Layout is ABI-sensitive for `gettimeofday`, select timeouts, BIO timestamps, and older BSD APIs.
