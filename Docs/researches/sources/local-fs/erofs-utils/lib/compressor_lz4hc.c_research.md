# File Research: sources/local-fs/erofs-utils/lib/compressor_lz4hc.c

## Purpose
LZ4HC compressor backend, registered as an optimizer for the LZ4 on-disk algorithm.

## Important Functions
- `lz4hc_compress_destsize()`: wraps `LZ4_compress_HC_destSize()`.
- `compressor_lz4hc_init()` / `compressor_lz4hc_exit()`: allocate/free `LZ4_streamHC`.
- `compressor_lz4hc_setlevel()`: validates level and defaults to `LZ4HC_CLEVEL_DEFAULT`.

## Interactions
- Compiled under `ENABLE_LZ4HC`.
- Shares on-disk algorithm id `Z_EROFS_COMPRESSION_LZ4` through the registry.

## Notes
Like normal LZ4, updates `sbi->lz4.max_distance`.
