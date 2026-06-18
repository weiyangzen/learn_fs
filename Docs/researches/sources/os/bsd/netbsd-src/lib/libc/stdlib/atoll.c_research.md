# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/atoll.c

Read completely: 64 lines.

Implements `atoll()` when `HAVE_ATOLL` is not provided by the build environment. It returns `strtoll(str, NULL, 10)` and provides a libc weak alias when building inside libc.

This supports host-tool and libc builds through conditional includes.
