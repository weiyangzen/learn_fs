# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putc.c

Provides function versions of `putc()` and `putc_unlocked()`. Both write one byte through `__sputc(c, fp)`, with the normal variant locking the target stream.

This is a thin wrapper around stdio’s buffered byte output path.
