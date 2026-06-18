# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strerror_r.c

Implements POSIX `strerror_r()` and internal `_strerror_lr()`. It copies a known `sys_errlist` entry or formats `"Unknown error: %d"` for unknown numbers, returns `EINVAL` for unknown errors, and returns `ERANGE` if the caller buffer is too small while preserving the caller’s original `errno`.

With NLS enabled, it lazily caches translated error strings and the unknown-error prefix in the locale cache using atomic compare-and-swap and memory barriers.
