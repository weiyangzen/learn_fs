# File Research: sources/local-fs/erofs-utils/lib/compressor_liblzma.c

## Purpose
Optional LZMA compressor backend using liblzma MicroLZMA.

## Main Structure
- `struct erofs_liblzma_context`: LZMA options and stream.

## Important Functions
- `erofs_compressor_liblzma_preinit()`: allocates context and initializes stream.
- `erofs_liblzma_compress_destsize()`: runs `lzma_microlzma_encoder()` and returns consumed input/output size.
- `erofs_compressor_liblzma_exit()`: ends stream and frees context.
- `erofs_compressor_liblzma_setlevel()`: supports normal presets and `>=100` extreme presets, max 109.
- `erofs_compressor_liblzma_setdictsize()`: chooses or validates dictionary size within EROFS LZMA limits.
- `erofs_compressor_liblzma_setextraopts()`: parses `lc=`, `lp=`, and `pb=` options.

## Interactions
- Compiled only under `HAVE_LIBLZMA`.
- Compression config dictionary size is later written by `compress.c`.

## Notes
Provides `compress_destsize` only; no whole-buffer `compress` callback.
