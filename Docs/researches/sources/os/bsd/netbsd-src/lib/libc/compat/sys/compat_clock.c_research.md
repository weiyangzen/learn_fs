# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_clock.c

Read completely: 98 lines.

This implements compatibility `clock_settime`, `clock_gettime`, and `clock_getres` using `timespec50`. Set converts input to native and calls `__clock_settime50`; get/res call current wrappers and convert results back to `timespec50`.

Security/reliability notes: get/res handle null result pointers by passing null downstream. Set accepts null and forwards null, matching the wrapper style.
