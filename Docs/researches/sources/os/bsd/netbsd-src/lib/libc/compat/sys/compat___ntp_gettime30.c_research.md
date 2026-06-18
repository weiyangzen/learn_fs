# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___ntp_gettime30.c

Read completely: 30 lines.

This implements `__ntp_gettime30`, calling `__ntp_gettime50` and converting the returned `ntptimeval` to `ntptimeval50` with 32-bit seconds and nanoseconds.

Security/reliability notes: no local validation; output timestamp seconds are narrowed to `int32_t`.
