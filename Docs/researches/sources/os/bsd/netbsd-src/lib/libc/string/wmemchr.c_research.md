# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemchr.c

Implements `wmemchr(s, c, n)`. It linearly scans `n` wide elements and returns a pointer to the first element equal to `c`, or NULL.

The returned pointer drops const via `__UNCONST`, matching the C API.
