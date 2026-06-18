# File Research: sources/local-fs/erofs-utils/lib/compressor.h

## Purpose
Internal compression backend interface.

## Main Types
- `struct erofs_compressor`: backend vtable with lifecycle, level/dict/extra option setters, and compression callbacks.
- `struct erofs_algorithm`: registry entry with name, backend pointer, on-disk algorithm id, and optimizer flag.
- `struct erofs_compress`: active compressor handle with superblock pointer, selected algorithm, threshold, level, dict size, and private data.

## Important Declarations
- Extern declarations for lz4, lz4hc, lzma, deflate, libdeflate, and libzstd compressors.
- Public internal API for compressor initialization, dispatch, exit, reset, and algorithm id lookup.

## Interactions
- Included by `compress.c`, `fsck/main.c`, and all compressor backend files.

## Notes
The interface supports both `compress_destsize` and whole-buffer `compress`; unaligned extent paths rely on backends that implement `compress`.
