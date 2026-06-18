# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/compr.c

## Purpose
Implements mkfs.ubifs data compression using LZO, zlib/deflate, no-compression fallback, and an optional mode that favors LZO unless zlib is sufficiently better.

## Main Entry Points
- `compress_data()` selects and runs a compressor, then falls back to uncompressed data for short input, compressor failure, or non-beneficial compression.
- `init_compression()` allocates LZO work memory and a temporary zlib output buffer.
- `destroy_compression()` frees buffers and reports accumulated compression errors.

## Compression Logic
`zlib_deflate()` uses raw deflate settings chosen to match the kernel crypto API. `lzo_compress()` uses `lzo1x_999_compress()`. `favor_lzo_compress()` runs both compressors, compares output sizes, and chooses LZO if it is no larger or if zlib's win is within `info_.favor_percent`; otherwise it copies the zlib result into the caller's output buffer.

## Dependencies
Depends on zlib, LZO, Linux types, `compr.h`, and `mkfs.ubifs.h` global configuration (`info_`, `UBIFS_MIN_COMPR_LEN`, `UBIFS_BLOCK_SIZE`, `favor_lzo`, `favor_percent`).

## Risks and Notes
The implementation is global-state based: buffers, error count, and `info_` are not instance-local. `compress_data()` returns the selected mkfs compression enum, not a conventional negative error code.
