# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_compress.c

## Purpose

`zio_compress.c` provides table-driven compression selection, compression execution, decompression execution, and test hooks for simulated decompression failure.

## Major Responsibilities

- Defines `zio_compress_table[]`, mapping compression IDs to names, levels, compressor functions, and decompressor functions.
- Resolves inherited/on compression settings through `zio_compress_select()`.
- Compresses ABD data through `zio_compress_data()`.
- Decompresses linear buffers through `zio_decompress_data_buf()`.
- Decompresses ABD data through `zio_decompress_data()`.

## Compression Table

Supported entries are:

- `inherit`
- `on`
- `uncompressed`
- `lzjb`
- `empty`
- `gzip-1` through `gzip-9`
- `zle`
- `lz4`

`on` maps to LZ4 when `SPA_FEATURE_LZ4_COMPRESS` is active, otherwise to the legacy default.

## Compression Behavior

`zio_compress_data()` first checks whether the entire source ABD is zero. If so, it returns `0`, signaling that no block allocation is needed.

For nonzero data:

- `ZIO_COMPRESS_EMPTY` returns the source length.
- Other compressors are given a target length of 87.5% of the source length.
- Compression functions require linear input, so the source ABD is borrowed into a temporary linear buffer.
- If compressed output does not beat the target length, the original source length is returned, meaning compression is not worthwhile.

## Decompression Behavior

`zio_decompress_data_buf()` validates the compression function and calls the table decompressor.

`zio_decompress_data()` borrows compressed ABD data into a temporary linear buffer, decompresses it, and returns the ABD buffer. Unexpected decompression failure after checksum verification is treated as severe: it saves a copy of the failed compressed buffer and panics. A tunable fault hook can then force an `EINVAL` return after decompression for testing.

## Fault/Test Hooks

- `zio_decompress_fail_fraction` can probabilistically force decompression failure returns.
- `zio_decompress_failed_buf` stores a copy of data that caused an unexpected decompression panic.

## Key Dependencies

- Compressor implementations from `sys/compress.h`.
- ABD borrow/return helpers.
- SPA feature detection for LZ4 default behavior.
- Used heavily by `zio_write_compress()` and read-side `zio_decompress()` in `zio.c`.

## Notes for Future Readers

- Returning `0` from compression means “all-zero block,” not a compressed byte count.
- Compression functions never consume ABDs directly in this implementation.
- Decompression failure is considered evidence of memory corruption or an internal fault because checksum verification should already have passed.
