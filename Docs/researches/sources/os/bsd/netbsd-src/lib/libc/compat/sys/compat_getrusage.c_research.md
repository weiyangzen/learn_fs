# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getrusage.c

Read completely: 63 lines.

This implements old `getrusage` returning `struct rusage50`. It calls `__getrusage50` into native `struct rusage`, then converts to the compatibility layout.

Security/reliability notes: direct wrapper; time and resource fields may narrow according to `rusage_to_rusage50`.
