# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_nanosleep.c

Read completely: 77 lines.

This implements old `nanosleep` using `timespec50`. It converts optional requested and remaining time pointers around `__nanosleep50`.

Security/reliability notes: null pointers are handled. Remaining time is converted back only on successful wrapper return.
