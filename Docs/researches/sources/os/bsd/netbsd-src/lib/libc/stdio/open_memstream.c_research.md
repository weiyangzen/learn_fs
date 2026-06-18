# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/open_memstream.c

Implements `open_memstream()` with a `funopen2()` cookie that tracks the caller’s `char **bufp`, `size_t *sizep`, current allocated length, and logical offset. Writes grow the buffer with `realloc()`, zero-fill new gaps, copy data at the current offset, and update `*sizep` to the lesser of length and offset.

Seeking supports `SEEK_SET`, `SEEK_CUR` for ftell-style queries, and bounded `SEEK_END`; invalid negative/overflow positions set `EINVAL` or `EOVERFLOW`. The returned stream is byte-oriented via `fwide(fp, -1)`.
