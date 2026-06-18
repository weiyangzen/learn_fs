# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkstemp.c

Implements `mkstemp(char *path)` as a safe temporary file creator through `GETTEMP(path, &fd, 0, 0, 0)`. It returns the exclusive-created read/write file descriptor or `-1`.

The file also provides a weak alias for `_mkstemp` when enabled and is conditionally compiled for nbtool builds.
