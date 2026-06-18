# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/buf.c

This file implements buffered block I/O for `cdfs` track reading and writing.

Key behavior:
- `bopen()` allocates a `Buf` with block size, block count, mode, data area, and device callback.
- `bread()` refills the buffer on cache miss at a block-aligned offset, then serves byte-range reads from the cached data.
- `bwrite()` appends write data into a block buffer and flushes complete buffered chunks through the callback.
- `bterm()` flushes a final partial write buffer and frees storage.

Important details:
- Read buffering is offset-aware; write buffering intentionally ignores offset and is sequential.
- Write flushes are in whole media blocks except the final partial flush, rounded up by `bterm()`.
- The callback receives block counts, not byte counts.

Filesystem relevance:
- Direct. This is the buffering layer under the `cdfs` 9P CD/DVD/BD filesystem server’s track files.
