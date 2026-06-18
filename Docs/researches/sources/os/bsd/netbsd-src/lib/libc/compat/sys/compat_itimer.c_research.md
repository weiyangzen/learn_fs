# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_itimer.c

Read completely: 82 lines.

This implements old `setitimer` and `getitimer` using `itimerval50`. Set converts optional new and old timer values around `__setitimer50`; get calls `__getitimer50` and converts the result back.

Security/reliability notes: null timer pointers are handled as optional where supported by the underlying API.
