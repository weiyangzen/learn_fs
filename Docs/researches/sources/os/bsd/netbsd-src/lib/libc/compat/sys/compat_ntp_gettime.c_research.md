# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_ntp_gettime.c

Read completely: 30 lines.

This implements old `ntp_gettime`, calling `__ntp_gettime50` and converting native nanoseconds to old microseconds in `ntptimeval30`.

Security/reliability notes: seconds narrow to `int32_t`, and nanosecond precision is reduced to microseconds.
