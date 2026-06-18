# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/refill.c

Implements `__srefill()`, the core byte-stream input refill path. It initializes stdio if needed, rejects EOF or non-readable streams, switches read/write streams from write mode to read mode with `__sflush()`, discards active ungetc buffers while restoring original unread data, creates a buffer if needed, and reads into it through the stream read callback.

Before reading from line-buffered or unbuffered streams, it flushes all line-buffered output streams via `_fwalk(lflush)` under `__sfp_lock`. It marks `__SEOF` on zero-byte reads and `__SERR` on read errors.
