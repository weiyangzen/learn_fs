# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/sched.h

Declares compatibility scheduler interval API.

It includes scheduler and compatibility time headers, then declares `sched_rr_get_interval(pid_t, struct timespec50 *)`.

This is time ABI compatibility for POSIX scheduling.
