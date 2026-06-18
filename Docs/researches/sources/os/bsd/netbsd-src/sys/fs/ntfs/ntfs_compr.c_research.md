# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_compr.c

Implements NTFS compression decompression for compressed attribute reads.

Key points:
- `ntfs_uncompblock()` decompresses one 4 KiB NTFS compression block.
  - Handles uncompressed blocks by copying payload and zero-filling the rest.
  - Handles compressed tag streams using back-reference offset/length pairs.
- `ntfs_uncompunit()` decompresses a full compression unit of 16 clusters by repeatedly calling `ntfs_uncompblock()`.

Dependencies:
- Uses `NTFS_COMPBLOCK_SIZE` and `NTFS_COMPUNIT_CL` from `ntfs_compr.h`.
- Used by `ntfs_readattr()` when an attribute has compression enabled and a compression algorithm set.

Risk/notes:
- The decoder assumes trusted kernel buffers and uses direct unaligned `u_int16_t` reads through `GET_UINT16`.
