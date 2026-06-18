# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/utime.h

Read completely: 51 lines.

This header defines legacy `struct utimbuf50` with 32-bit access and modification times and declares the old `utime` entry point plus newer `__utime50`. It includes machine ANSI definitions and cdefs for ABI-compatible prototypes.

Important interactions: bridges old callers using 32-bit `time_t` to the current `struct utimbuf` implementation.

Security/reliability notes: no executable logic. Time truncation is inherent when converting current time values into `int32_t`.
