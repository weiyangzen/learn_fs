<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/memstream.c -->
# sources/user-network-fs/nfs-ganesha/src/os/freebsd/memstream.c

## Purpose
This file implements `open_memstream()` on FreeBSD using `funopen()`, providing a GNU-like memory stream API where unavailable.

## Important APIs, Types, and Functions
`struct memstream` stores pointers to the caller's buffer pointer and length, plus the current stream offset. `memstream_grow()` reallocates the caller buffer with one extra byte and zero-fills newly exposed memory. `memstream_read()`, `memstream_write()`, `memstream_seek()`, and `memstream_close()` implement the `funopen()` callbacks. `open_memstream(char **cp, size_t *lenp)` initializes outputs, allocates the cookie, and returns a `FILE *`.

## Control Flow
Opening initializes `*cp = NULL`, `*lenp = 0`, allocates a cookie, and calls `funopen()`. Reads and writes grow the backing buffer to cover the requested range, copy bytes, and advance `offset`. Seek updates `offset` based on `SEEK_SET`, `SEEK_CUR`, or `SEEK_END`. Close frees only the cookie; the caller retains ownership of `*cp`.

## State and Persistence Behavior
The buffer and length are caller-visible and persist after `fclose()` until the caller frees the buffer. Internal offset lives in the stream cookie and disappears on close.

## Dependencies and Integration Points
It depends on FreeBSD `funopen()`, stdio, and Ganesha memory wrappers (`gsh_malloc`, `gsh_realloc`, `gsh_free`). It provides compatibility for code expecting `open_memstream()`.

## Risks and Edge Cases
`memstream_grow()` does not handle allocation failure from `gsh_realloc()` locally. The zero-fill starts at `buf + *lenp + 1`, leaving the byte at old length untouched until write behavior sets it; NUL-termination semantics should be verified. `memstream_seek()` does not reject invalid `whence` or negative positions that wrap in `size_t`. Callback signatures use `int len`, which can truncate very large sizes.

## Test Signals
Tests should write strings and binary data, seek forward/backward, read from sparse regions, close and inspect `*cp`/`*lenp`, verify NUL termination, and simulate allocation failure if the memory wrapper supports it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/freebsd/memstream.c -->
