# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sigtimedwait.c

Read completely: 75 lines.

This implements old `sigtimedwait` and `__sigtimedwait` with `timespec50` timeout. It converts a non-null timeout to native `timespec` and calls `____sigtimedwait50`; null timeout is passed through.

Security/reliability notes: direct wrapper; signal set and siginfo pointers are forwarded unchanged.
