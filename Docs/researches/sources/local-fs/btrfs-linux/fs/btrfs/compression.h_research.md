# File Research: sources/local-fs/btrfs-linux/fs/btrfs/compression.h

## Purpose

Declares the public Btrfs compression interface shared by core filesystem code and compression algorithm implementations.

## Main Responsibilities

- Defines compressed extent size limits and compression chunk sizing.
- Defines `struct compressed_bio`, the wrapper around `struct btrfs_bio` used for compressed IO.
- Declares workspace manager structures and generic workspace helpers.
- Declares common compression/decompression entry points.
- Declares algorithm-specific zlib, lzo, and zstd functions.
- Provides inline cleanup and utility helpers.

## Key Definitions

- `BTRFS_MAX_COMPRESSED`: maximum on-disk compressed extent size, 128 KiB.
- `BTRFS_MAX_UNCOMPRESSED`: maximum uncompressed input extent size, 128 KiB.
- `BTRFS_COMPRESSION_CHUNK_SIZE`: maximum single worker compression chunk, 512 KiB.
- `BTRFS_MAX_COMPRESSED_PAGES`: page-count form of the compressed extent cap.
- `BTRFS_ZLIB_DEFAULT_LEVEL`: default zlib level 3.
- `struct compressed_bio`: stores file start, inode byte length, compression type, writeback flag, original read bio pointer, and embedded `btrfs_bio`.
- `struct workspace_manager`: idle workspace list, lock, counters, and wait queue.
- `struct btrfs_compress_levels`: min/max/default level metadata.

## Important Functions And Macros

- `cb_to_fs_info()` returns the filesystem from a compressed bio.
- `btrfs_calc_input_length()` computes the valid input bytes in a folio for a compression range.
- `cleanup_compressed_bio()` frees all compressed folios in a bio and releases the bio.
- Public core functions include `btrfs_compress_bio()`, `btrfs_submit_compressed_read()`, `btrfs_submit_compressed_write()`, `btrfs_decompress()`, `btrfs_decompress_buf2page()`, and `btrfs_compress_heuristic()`.
- Algorithm declarations expose compressor, decompressor, workspace allocation, workspace free, and zstd manager functions.

## Integration Points

This header is included by compression algorithm files, the core compression implementation, defrag code, ordered IO paths, and code that parses or validates compression configuration. It depends on `bio.h`, `fs.h`, and `btrfs_inode.h` for embedded Btrfs types.

## Invariants And Risks

- The size constants are core on-disk/runtime assumptions for compressed extents.
- `compressed_bio` requires the embedded `btrfs_bio` to remain last because allocation uses `offsetof(struct compressed_bio, bbio.bio)`.
- `cleanup_compressed_bio()` assumes all bio folios were allocated through the compression folio allocator.
- Level validity is delegated to per-algorithm `btrfs_compress_levels` definitions.

## Testing Notes

Compile coverage is important because this header binds multiple compression backends. Runtime testing should verify cleanup on failed compression, all algorithm workspace paths, inline decompression callers, and compressed read/write end IO.
