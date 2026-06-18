# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemcpy.c

Implements `wmemcpy(d, s, n)` by calling `memcpy(d, s, n * sizeof(wchar_t))` and casting the result back to `wchar_t *`.

Overlap behavior follows `memcpy`, so overlapping ranges are not supported.
