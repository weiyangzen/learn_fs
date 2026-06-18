# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/clrerr.c

Read completely: 58 lines.

This file implements the function form of `clearerr`. It locks the stream, calls the internal `__sclearerr(fp)`, and unlocks.

Important interactions: uses `reentrant.h` locking and `local.h` stdio internals.

Security/reliability notes: assumes a non-NULL `FILE *`; diagnostics use `_DIAGASSERT`.
