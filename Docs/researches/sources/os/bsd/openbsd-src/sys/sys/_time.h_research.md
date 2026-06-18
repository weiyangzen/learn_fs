# File Research: sources/os/bsd/openbsd-src/sys/sys/_time.h

Purpose: Defines core time types, clock constants, and POSIX timer structures.

Key contents:
- `CLOCKS_PER_SEC` is set to 100.
- BSD-visible macros encode/decode per-process and per-thread clock IDs.
- Defines `time_t` from `__time_t` when visible.
- Defines `struct timespec` with seconds and nanoseconds.
- Defines clock IDs for realtime, process CPU, monotonic, thread CPU, uptime, and boottime.
- Defines `struct itimerspec` and relative/absolute timer flags.

Filesystem relevance:
- VFS metadata operations use `timespec` for atime, mtime, ctime, and timestamp updates.
