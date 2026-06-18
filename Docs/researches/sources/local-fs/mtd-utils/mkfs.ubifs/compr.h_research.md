# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/compr.h

## Purpose
Declares the mkfs.ubifs compression interface and compression type identifiers.

## Main Definitions
- `WORST_COMPR_FACTOR` is the assumed maximum expansion factor for temporary compressor output buffers.
- `enum compression_type` defines `MKFS_UBIFS_COMPR_NONE`, `MKFS_UBIFS_COMPR_LZO`, and `MKFS_UBIFS_COMPR_ZLIB`.
- Declares `compress_data()`, `init_compression()`, and `destroy_compression()`.

## Dependencies
Requires standard `size_t` visibility from includers and is implemented by `compr.c`.

## Risks and Notes
The enum is mkfs-specific and should be mapped carefully to on-media UBIFS compression constants by callers.
