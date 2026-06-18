# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/stdio.c

Provides low-level stdio cookie operations for normal file-descriptor-backed streams: `__sread()`, `__swrite()`, `__sseek()`, and `__sclose()`. Reads update the known offset on success; seeks set or clear `__SOFF`; closes call `close()`.

`__swrite()` handles append mode by seeking to end before writes when needed, clears offset knowledge before writing, and tolerates `ESPIPE` by disabling append tracking for unseekable descriptors.
