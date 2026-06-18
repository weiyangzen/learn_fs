# File Research: sources/os/linux/linux-stable/fs/jffs2/read.c

This file implements data reads from JFFS2 raw inode nodes and logical inode ranges.

Key responsibilities:
- `jffs2_read_dnode()` reads a raw inode header, verifies header/node CRC, handles an old zero-compression hole-node size bug, reads compressed or uncompressed data, verifies data CRC, decompresses when needed, and copies requested subranges into the caller buffer.
- Optimizes the full uncompressed-node case by reading directly into the destination buffer.
- Allocates intermediate compressed and decompressed buffers only when partial reads or compression require them.
- Treats `JFFS2_COMPR_ZERO` nodes as holes and fills the requested range with zeroes.
- `jffs2_read_inode_range()` walks the inode fragment tree, fills missing ranges and explicit hole fragments with zeroes, and dispatches real fragments to `jffs2_read_dnode()`.

Important interactions:
- Uses raw node refs from the fragment tree built by `readinode.c`.
- Uses `jffs2_flash_read()` so pending write-buffer contents can be visible to reads.
- Uses `jffs2_decompress()` and compressor identifiers stored in raw inode nodes.

Notable invariants and risks:
- Header and data CRC failures return `-EIO`; `jffs2_read_inode_range()` zeroes the failed read span before returning the error.
- Partial compressed reads must decompress the whole logical dnode before copying the requested slice.
- The code notes that a single physical node referenced by multiple fragments may be read more than once.
