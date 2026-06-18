# File Research: sources/local-fs/erofs-utils/lib/compressor.c

## Purpose
Central registry and dispatch layer for EROFS compression backends.

## Main Data
- `erofs_algs[]`: maps user-visible names to compressor implementations and on-disk algorithm ids.
- Registered names include `lz4`, optional `lz4hc`, `lzma`, `deflate`, optional `libdeflate`, and `zstd`.

## Important Functions
- `z_erofs_get_compress_algorithm_id()`: returns on-disk algorithm id for a handle.
- `z_erofs_list_supported_algorithms()`: lists unique supported algorithm names, masking duplicate ids/optimizers.
- `z_erofs_list_available_compressors()`: iterates compiled-in compressor entries.
- `erofs_compress_destsize()` and `erofs_compress()`: dispatch to backend callbacks.
- `erofs_compressor_init()`: validates requested algorithm, level, dict size, extra options, runs preinit/setters/init, and binds selected algorithm.
- `erofs_compressor_exit()` / `erofs_compressor_reset()`: backend lifecycle dispatch.

## Interactions
- Used by mkfs compression setup and fsck help/version output.
- Backend implementations are in `compressor_*.c`.

## Notes
Optimizer aliases such as `lz4hc` and `libdeflate` can share an on-disk algorithm id with a base algorithm while exposing a different implementation.
