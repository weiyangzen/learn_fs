# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wmemset.c

Implements `wmemset(s, c, n)`. It writes wide character `c` into `n` consecutive elements and returns the original pointer.

This is a simple scalar loop.
