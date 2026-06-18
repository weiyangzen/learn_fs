# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_adjtime.c

Read completely: 77 lines.

This implements old `adjtime` using `timeval50` inputs and outputs. It converts optional delta and old-delta pointers to native `timeval`, calls `__adjtime50`, and converts the remainder back on success.

Security/reliability notes: null input/output pointers are handled. Timestamp narrowing happens only for the returned compatibility structure.
