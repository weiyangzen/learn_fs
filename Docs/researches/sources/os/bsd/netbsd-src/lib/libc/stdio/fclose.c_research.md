# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fclose.c

Read completely: 77 lines.

This file implements `fclose`. It rejects already-free streams with `EBADF`, locks the stream, frees wide I/O state, flushes pending writes, calls the stream close hook, frees allocated buffers/ungetc/line buffers, unlocks, and marks the `FILE` slot reusable.

Important interactions: depends on `__sflush`, stream operation hooks, `WCIO_FREE`, `FREEUB`, and `FREELB`.

Security/reliability notes: after close it deliberately poisons `_file`, `_flags`, `_r`, and `_w` to reduce accidental reuse.
