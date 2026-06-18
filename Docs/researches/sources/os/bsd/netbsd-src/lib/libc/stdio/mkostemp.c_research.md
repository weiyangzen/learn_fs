# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkostemp.c

Implements `mkostemp(char *path, int oflags)`. It delegates to `GETTEMP()` with no suffix and file creation enabled, returning the created file descriptor or `-1`.

Allowed `oflags` are enforced inside `GETTEMP()`, not in this wrapper.
