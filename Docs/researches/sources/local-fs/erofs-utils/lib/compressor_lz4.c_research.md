# File Research: sources/local-fs/erofs-utils/lib/compressor_lz4.c

## Purpose
LZ4 compressor backend.

## Important Functions
- `lz4_compress_destsize()`: wraps `LZ4_compress_destSize()`, updating consumed source size.
- `compressor_lz4_init()`: updates `sbi->lz4.max_distance` to at least `LZ4_DISTANCE_MAX`.
- `compressor_lz4_exit()`: no-op success.

## Interactions
- Registered as `lz4` when LZ4 support is enabled.
- LZ4 max distance is written/read as part of EROFS compression configuration.

## Notes
No compression level or private stream is used.
