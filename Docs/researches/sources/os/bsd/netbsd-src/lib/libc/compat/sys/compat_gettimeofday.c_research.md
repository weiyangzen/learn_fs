# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_gettimeofday.c

Read completely: 62 lines.

This implements old `gettimeofday` with `timeval50`. It calls `__gettimeofday50` into native `timeval` and converts to `timeval50`.

Security/reliability notes: the code converts into `tv50` unconditionally after success, so callers must provide a valid output pointer for this ABI.
