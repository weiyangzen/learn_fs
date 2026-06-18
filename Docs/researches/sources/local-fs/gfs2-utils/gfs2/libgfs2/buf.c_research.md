# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/buf.c

This file implements simple block buffer allocation, reading, writing, release, discard-free, and metadata-type detection for libgfs2.

Functions:
- `lgfs2_bget()` allocates a `struct lgfs2_buffer_head` plus one block-sized data buffer and initializes block number, superblock pointer, and data pointer.
- `__lgfs2_bread()` allocates a buffer and reads one filesystem block with `pread()`, reporting caller/line on failure.
- `lgfs2_bwrite()` writes a modified buffer to its block offset with `pwrite()` and clears `b_modified`.
- `lgfs2_brelse()` writes modified buffers, removes them from `b_altlist` if linked, marks the block number invalid, and frees memory.
- `lgfs2_bfree()` frees without writing and nulls the caller’s pointer.
- `lgfs2_get_block_type()` reads a `gfs2_meta_header` and returns its metatype if the magic matches.

Dependencies include `libgfs2.h`, POSIX I/O, and GFS2 endian helpers.

Risks and notes:
- `lgfs2_brelse()` auto-writes modified buffers, so callers must use `lgfs2_bfree()` when they need discard semantics.
- Partial I/O is treated as failure.
- There is only a debug print for double-free detection via block number `-1`.
