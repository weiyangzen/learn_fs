# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sched.c

Read completely: 56 lines.

This implements old `sched_rr_get_interval`. It ignores the PID, sets seconds to zero, and sets nanoseconds from `sysconf(_SC_SCHED_RT_TS) * 1000`.

Security/reliability notes: no syscall is used. If `sysconf` fails or returns an unexpected value, the result is passed through arithmetically without local error handling.
