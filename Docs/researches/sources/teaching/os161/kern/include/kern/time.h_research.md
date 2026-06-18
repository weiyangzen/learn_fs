# File Research: sources/teaching/os161/kern/include/kern/time.h

Defines time ABI structures.

Key contents:
- `struct timeval` with seconds and microseconds.
- `struct timespec` with seconds and nanoseconds.
- Interval timer constants and `struct itimerval`.

Relevance:
- Used by clock APIs, resource usage, stat timestamps, and time-related syscalls.
