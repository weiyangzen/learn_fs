# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_timer.c

Read completely: 83 lines.

This implements old `timer_settime` and `timer_gettime` using `itimerspec50`. Set converts optional new and old timer specs around `__timer_settime50`; get calls `__timer_gettime50` and converts the result back.

Security/reliability notes: direct wrapper; null optional pointers are handled.
