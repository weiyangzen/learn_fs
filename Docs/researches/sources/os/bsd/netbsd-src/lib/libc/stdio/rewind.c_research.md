# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/rewind.c

Implements `rewind(FILE *)`. It locks the stream, performs `fseek(fp, 0L, SEEK_SET)`, clears error and EOF state with `__sclearerr()`, then unlocks.

The function deliberately ignores the seek return value, matching the standard `rewind()` interface.
