# File Research: sources/os/bsd/freebsd-src/sys/sys/_timespec.h

Nanosecond-resolution time structure.

Key elements:
- Defines `time_t` if not already declared.
- Defines `struct timespec` with seconds and nanoseconds.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Common timestamp ABI used by filesystems, timers, semaphores, AIO, and stat-like interfaces.
