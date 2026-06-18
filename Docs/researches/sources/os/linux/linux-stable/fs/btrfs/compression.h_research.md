# File Research: sources/os/linux/linux-stable/fs/btrfs/compression.h

## Purpose
Defines the public interface, shared constants, and core structures for Btrfs compression support.

## Main Responsibilities
- Define maximum compressed and uncompressed extent sizes.
- Define compression chunk size and default zlib level.
- Define `struct compressed_bio`, the wrapper around `struct btrfs_bio`.
- Define workspace manager types and compression level metadata.
- Declare compression lifecycle, read/write, workspace, heuristic, and algorithm-specific functions.
- Provide inline helpers for compressed bio cleanup and range accounting.

## Key Definitions
- `BTRFS_MAX_COMPRESSED`: 128 KiB maximum compressed data stored on disk.
- `BTRFS_MAX_COMPRESSED_PAGES`: maximum order-0 pages needed for a compressed extent.
- `BTRFS_COMPRESSION_CHUNK_SIZE`: 512 KiB maximum single-worker compression chunk.
- `BTRFS_MAX_UNCOMPRESSED`: 128 KiB maximum input size for one compressed extent.
- `BTRFS_ZLIB_DEFAULT_LEVEL`: default zlib compression level, `3`.
- `BTRFS_NR_WORKSPACE_MANAGERS`: same as `BTRFS_NR_COMPRESS_TYPES`, with type 0 used for heuristic workspaces.

## Important Interfaces
- Lifecycle: `btrfs_alloc_compress_wsm()`, `btrfs_free_compress_wsm()`, `btrfs_init_compress()`, `btrfs_exit_compress()`.
- Generic compression: `btrfs_compress_level_valid()`, `btrfs_decompress()`, `btrfs_decompress_buf2page()`, `btrfs_compress_str2level()`, `btrfs_compress_heuristic()`, `btrfs_compress_bio()`.
- Compressed I/O: `btrfs_alloc_compressed_write()`, `btrfs_submit_compressed_write()`, `btrfs_submit_compressed_read()`.
- Folio/workspace management: `btrfs_alloc_compr_folio()`, `btrfs_free_compr_folio()`, `btrfs_get_workspace()`, `btrfs_put_workspace()`.

## Invariants
`compressed_bio::bbio` must remain last because allocation embeds the bio object. Compressed extent size constants are page-aligned. Callers that attach compressed folios to compressed bios must release them with `btrfs_free_compr_folio()`. Zstd uses custom workspace manager hooks unlike zlib/lzo/heuristic generic managers.
