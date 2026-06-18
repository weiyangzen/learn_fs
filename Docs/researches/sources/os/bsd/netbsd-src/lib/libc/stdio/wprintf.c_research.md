# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wprintf.c

Read completely: 69 lines.

Implements variadic `wprintf()` and `wprintf_l()`. Both gather a `va_list`, call `vfwprintf()` or `vfwprintf_l()` on `stdout`, end the list, and return the delegated result.

This is a thin public API wrapper; stream behavior is entirely handled by the lower-level wide formatter.
