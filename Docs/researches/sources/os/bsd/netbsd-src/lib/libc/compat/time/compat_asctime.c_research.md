# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_asctime.c

Read completely: 33 lines.

This builds compatibility `ctime_r` and `ctime_rz` by redefining `timeval`, `timespec`, and `time_t` to the 50/32-bit compatibility types, then including the shared `time/asctime.c` implementation.

Important interactions: source inclusion reuses the real implementation while compiling it for the old ABI type universe.

Security/reliability notes: inherits behavior from `asctime.c`; timestamp range is limited by `int32_t time_t`.
