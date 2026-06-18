# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getchar.c

Provides function versions of `getchar()` and `getchar_unlocked()`. Both read from `stdin` via `__sgetc()`, with the normal variant locking `stdin`.

This is a minimal adapter around the same byte input machinery used by `getc.c`.
