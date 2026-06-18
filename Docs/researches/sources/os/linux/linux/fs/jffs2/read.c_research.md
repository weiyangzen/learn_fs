# File Research: sources/os/linux/linux/fs/jffs2/read.c

## Role

Implements reading data from JFFS2 raw inode nodes and logical inode ranges.

## Key Responsibilities

- `jffs2_read_dnode()` reads a raw inode header, validates header/node CRC, handles an old zero-compression hole-node size bug, reads node payload, validates data CRC, decompresses if needed, and copies requested subranges.
- Optimizes full uncompressed reads by reading directly into the caller buffer.
- Allocates compressed and decompressed scratch buffers only when partial reads or compression require them.
- Handles `JFFS2_COMPR_ZERO` by zero-filling the requested range.
- `jffs2_read_inode_range()` walks the inode fragment tree, zero-fills gaps and hole fragments, and dispatches real fragments to `jffs2_read_dnode()`.

## Important Interactions

- Consumes raw node refs and fragment trees built by `readinode.c`.
- Uses `jffs2_flash_read()` so pending write-buffer data can be visible to reads.
- Uses `jffs2_decompress()` with compression identifiers stored in raw inode nodes.

## Invariants and Risks

- Header or data CRC mismatch returns `-EIO`.
- On read error, `jffs2_read_inode_range()` zeroes the failed span before returning.
- Partial compressed reads must decompress the full logical dnode before copying the requested slice.
- A single physical node referenced by multiple fragments may be read more than once.
