# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vprintf.c

Implements `vprintf()` and `vprintf_l()` as direct calls to `vfprintf(stdout, ...)` and `vfprintf_l(stdout, loc, ...)`. It adds no formatting logic.

The locale variant is weak-aliased as `vprintf_l -> _vprintf_l`.
