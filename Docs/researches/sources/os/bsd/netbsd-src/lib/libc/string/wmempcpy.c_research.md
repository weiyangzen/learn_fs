# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmempcpy.c

Implements `wmempcpy(dst, src, len)`. It calls `wmemcpy()` for `len` wide elements and returns `dst + len`.

Like `wmemcpy`, it is not for overlapping ranges.
