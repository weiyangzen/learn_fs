# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vwprintf.c

Read completely: 56 lines.

Implements `vwprintf_l()` and `vwprintf()` as direct wrappers around `vfwprintf_l(stdout, ...)` and `vfwprintf(stdout, ...)`.

There is no independent formatting logic here; all behavior, locking, orientation, locale conversion, and error handling are delegated to the `vfwprintf` family.
