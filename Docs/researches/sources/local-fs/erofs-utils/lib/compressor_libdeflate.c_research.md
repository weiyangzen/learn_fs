# File Research: sources/local-fs/erofs-utils/lib/compressor_libdeflate.c

## Purpose
Optional DEFLATE compressor backend using libdeflate.

## Main Structure
- `struct erofs_libdeflate_context`: libdeflate compressor, temporary fit-block buffer, buffer size, and last chosen uncompressed size.

## Important Functions
- `libdeflate_compress()`: compresses a full input into a bounded destination; returns `-ENOSPC` when it does not fit.
- `libdeflate_compress_destsize()`: searches for the largest input prefix fitting the destination, using ratio estimation and binary fallback.
- `compressor_libdeflate_init()` / `compressor_libdeflate_exit()`: allocate/free context and libdeflate compressor.
- `compressor_libdeflate_reset()`: clears last-size heuristic.
- `erofs_compressor_libdeflate_setlevel()`: default level 1, max 12.

## Special Behavior
- Ensures the first compressed byte is not zero in some cases so EROFS zero-padding length detection remains valid for DEFLATE streams.

## Interactions
- Registered as optimizer for on-disk DEFLATE when `HAVE_LIBDEFLATE` is enabled.

## Notes
Supports both whole-buffer `compress` and `compress_destsize`, making it usable for unaligned compressed extents.
