# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkdtemp.c

Implements `mkdtemp(char *path)` using `GETTEMP(path, NULL, 1, 0, 0)`. On success it returns the caller path after creating the directory; on failure it returns `NULL`.

The wrapper is conditionally compiled for nbtool compatibility when the host lacks `mkdtemp`.
