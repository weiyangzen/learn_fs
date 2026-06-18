# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkostemps.c

Implements `mkostemps(char *path, int slen, int oflags)`. It delegates to `GETTEMP()` with a caller-specified suffix length and requested open flags, returning the new fd or `-1`.

It is the suffix-aware variant of `mkostemp()`.
