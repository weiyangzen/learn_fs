# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkstemps.c

Implements `mkstemps(char *path, int slen)` using `GETTEMP()` with file creation and a fixed suffix length. It returns the created fd or `-1`.

This is the non-`oflags` suffix-aware temporary file wrapper.
