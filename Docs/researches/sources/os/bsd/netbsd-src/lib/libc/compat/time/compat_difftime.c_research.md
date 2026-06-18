# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_difftime.c

Read completely: 54 lines.

This builds compatibility `difftime` by redefining time-related types to compatibility layouts and including the shared `time/difftime.c`.

Security/reliability notes: the function operates over `int32_t time_t` in this build, so range is the historical ABI range.
