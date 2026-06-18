# File Research: sources/local-fs/erofs-utils/lib/compressor_libzstd.c

## Purpose
Optional Zstandard compressor backend using libzstd.

## Main Structure
- `struct erofs_libzstd_context`: ZSTD compression context and temporary fit-block buffer.

## Important Functions
- `libzstd_compress()`: whole-buffer `ZSTD_compress2()` wrapper.
- `libzstd_compress_destsize()`: searches largest input prefix that fits destination.
- `compressor_libzstd_init()` / `compressor_libzstd_exit()`: allocate/free ZSTD context and temp buffer.
- `erofs_compressor_libzstd_setlevel()`: validates level up to 22.
- `erofs_compressor_libzstd_setdictsize()`: requires power-of-two dictionary/window size within EROFS zstd max.

## Behavior
- Sets `ZSTD_c_compressionLevel` and `ZSTD_c_windowLog`.
- Emits a one-time warning that the libzstd compressor is experimental and fit-block is not upstream-supported.

## Interactions
- Registered under name `zstd` when `HAVE_LIBZSTD` is enabled.
- Supports whole-buffer compression and destination-size fitting.

## Notes
The backend uses window log as the dictionary-size representation used by EROFS config metadata.
