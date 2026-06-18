# File Research: sources/local-fs/erofs-utils/lib/compressor_deflate.c

## Purpose
Built-in DEFLATE compressor backend using the local `kite_deflate` implementation.

## Important Functions
- `deflate_compress_destsize()`: delegates to `kite_deflate_destsize()`.
- `compressor_deflate_init()` / `compressor_deflate_exit()`: create and destroy kite deflate state.
- `erofs_compressor_deflate_setlevel()`: validates level up to 9, default 1.
- `erofs_compressor_deflate_setdictsize()`: validates dictionary size, fixed max/default 32 KiB.

## Backend Capabilities
- Provides `compress_destsize`.
- Does not provide whole-buffer `compress`.
- On-disk algorithm id is `Z_EROFS_COMPRESSION_DEFLATE` via registry.

## Interactions
- Always added to `liberofs_la_SOURCES` with `kite_deflate.c`.

## Notes
Returns `-EFAULT` if the underlying kite compressor returns a nonpositive compressed size.
