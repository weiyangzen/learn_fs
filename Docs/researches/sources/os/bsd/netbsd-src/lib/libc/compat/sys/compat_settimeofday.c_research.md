# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_settimeofday.c

Read completely: 65 lines.

This implements old `settimeofday` with a `timeval50` pointer. It converts the supplied time to native `timeval` and calls `__settimeofday50`.

Security/reliability notes: unlike several other time wrappers, it dereferences/converts `tv50` unconditionally, so this compatibility ABI expects a non-null time pointer.
