# File Research: sources/os/linux/linux/fs/erofs/compress.h

Declares EROFS decompression request structures, decompressor interfaces, and shared compression helpers.

Key behavior:
- `z_erofs_decompress_req` describes input/output page arrays, offsets, sizes, algorithm, in-place/partial/fill-gap flags, and allocation policy.
- `z_erofs_decompressor` defines optional config/init/exit hooks plus the decompression callback.
- Defines markers for short-lived and preallocated folios.
- Provides helpers to identify/recycle short-lived decompression pages.
- Declares LZMA, DEFLATE, ZSTD, decompressor table, stream-buffer switching, compressed-size fixup, subsystem init/exit, and crypto acceleration hooks.
- Provides no-op crypto engine helpers when acceleration is disabled.

Important interactions:
- Shared by all decompressor implementations and compressed-data read paths.
- The request structure is the ABI between zdata/zmap code and algorithm-specific decoders.
