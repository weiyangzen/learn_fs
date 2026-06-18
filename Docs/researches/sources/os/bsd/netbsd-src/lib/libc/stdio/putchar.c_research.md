# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putchar.c

Provides function versions of `putchar()` and `putchar_unlocked()`. Both write to `stdout` through `__sputc()`, with locking only in `putchar()`.

It is the stdout-specific analogue of `putc.c`.
