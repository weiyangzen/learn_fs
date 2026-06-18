# File Research: sources/local-fs/erofs-utils/lib/decompress.c

## Purpose
Userspace decompression dispatcher for EROFS compressed data and parser for on-disk compression configuration records.

## Supported Paths
- Shifted/interlaced uncompressed layouts.
- LZ4 when enabled.
- LZMA when liblzma is enabled.
- DEFLATE through Intel QPL when enabled and suitable, otherwise libdeflate or zlib.
- Zstandard when libzstd is enabled.

## Important Functions
- `z_erofs_fixup_insize()`: skips leading zero padding in padded compressed input.
- `z_erofs_decompress_lz4()`, `z_erofs_decompress_lzma()`, `z_erofs_decompress_deflate()`, `z_erofs_decompress_zstd()`, `z_erofs_decompress_qpl()`: algorithm-specific decode paths.
- `z_erofs_decompress()`: top-level dispatch by `rq->alg`.
- `z_erofs_load_lz4_config()`: loads LZ4 max distance and max pcluster blocks.
- `z_erofs_load_deflate_config()`: under QPL, decides whether QPL can handle the DEFLATE history window.
- `z_erofs_parse_cfgs()`: parses superblock compression algorithm bitmask and per-algorithm config metadata.

## Interactions
- Called by `data.c` and fsck data verification.
- Reads variable-sized compression configs via `erofs_read_metadata()`.
- Uses `erofs_get_available_processors()` for QPL job cache sizing.

## Notes
Many decoders allocate a temporary full output buffer when `decodedskip` is nonzero. Partial decoding behavior varies by backend.
