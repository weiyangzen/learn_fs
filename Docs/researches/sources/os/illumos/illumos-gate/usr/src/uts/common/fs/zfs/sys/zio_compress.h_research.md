# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_compress.h

Defines ZIO compression algorithm IDs, compression/decompression function signatures, compression info table, algorithm entry points, and generic compression/decompression wrappers.

Key elements:
- `enum zio_compress` includes inherit, on, off, LZJB, empty, gzip levels 1-9, ZLE, LZ4, and functions sentinel.
- `zio_compress_func_t`, `zio_decompress_func_t`, and `zio_decompress_abd_func_t` define common algorithm signatures.
- `zio_compress_info_t` stores name, level, compress function, and decompress function.
- Declares LZJB, gzip, ZLE, and LZ4 routines.
- Generic wrappers operate on ABD input or raw buffers.

Main dependencies and interactions:
- Includes `sys/abd.h`.
- Used by ZIO write compression and read decompression pipelines.

Implementation notes:
- ABD-specific decompression signature exists to support compressed ARC plus scatter ABDs without requiring every algorithm to implement it.
