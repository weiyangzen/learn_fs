# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getc.c

Provides function versions of the `getc` and `getc_unlocked` macros. `getc()` locks the stream, calls `__sgetc(fp)`, unlocks, and returns the character or EOF; `getc_unlocked()` calls `__sgetc()` without locking.

The file relies on the stdio internal fast-path macro/helper definitions from `local.h` and uses `_DIAGASSERT()` for null stream diagnostics.
