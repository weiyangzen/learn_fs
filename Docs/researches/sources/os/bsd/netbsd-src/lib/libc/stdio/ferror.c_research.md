# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ferror.c

Read completely: 65 lines.

This file implements the function form of `ferror`. It locks the stream, reads error status through `__sferror(fp)`, unlocks, and returns it.

Important interactions: simple public wrapper over stdio internal flags.

Security/reliability notes: assumes valid `FILE *`; no error recovery is attempted.
