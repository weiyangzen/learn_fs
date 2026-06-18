# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strerror_ss.c

Implements stack-smashing-safe variants `strerror_r_ss()` and `strerror_ss()`. The intent is to copy a known `sys_errlist` entry or format an unknown-error message with `snprintf_ss()` into a caller/static buffer.

Notable caveat: the condition `if (num >= 0 || num < sys_nerr)` is always true for normal positive `sys_nerr`, so out-of-range values can index `sys_errlist[num]` instead of taking the unknown-error path.
