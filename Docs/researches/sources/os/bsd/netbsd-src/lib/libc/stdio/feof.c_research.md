# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/feof.c

Read completely: 65 lines.

This file implements the function form of `feof`. It locks the stream, reads EOF status via `__sfeof(fp)`, unlocks, and returns the result.

Important interactions: wrapper around the macro/internal status bit.

Security/reliability notes: no side effects beyond locking.
