# File Research: sources/os/linux/linux/fs/btrfs/compression.h

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
- `BTRFS_NR_WORKSPACE_MANAGERS`: same as `BTRFS_NR_COMPRESS_TYPES`, with compression type 0 used for heuristic workspaces.

## Key Types

- `struct compressed_bio`:
  - `start`: inode offset of the compressed extent.
  - `len`: logical file bytes covered.
  - `compress_type`: algorithm identifier.
  - `writeback`: whether completion should clear page-cache writeback.
  - `orig_bbio`: original destination bio for reads.
  - `bbio`: embedded Btrfs bio, intentionally last.

- `struct workspace_manager`:
  - Idle workspace list.
  - Spinlock.
  - Free workspace count.
  - Atomic total workspace count.
  - Waitqueue for waiters.

- `struct btrfs_compress_levels`:
  - Minimum, maximum, and default levels for an algorithm.

## Important Helpers

- `cb_to_fs_info()` resolves the filesystem from a compressed bio.
- `btrfs_calc_input_length()` computes how much of a folio participates in a requested input range.
- `cleanup_compressed_bio()` frees all compressed folios attached to the embedded bio and drops the bio.

## Declared Interfaces

- Lifecycle:
  - `btrfs_alloc_compress_wsm()`
  - `btrfs_free_compress_wsm()`
  - `btrfs_init_compress()`
  - `btrfs_exit_compress()`

- Generic compression:
  - `btrfs_compress_level_valid()`
  - `btrfs_decompress()`
  - `btrfs_decompress_buf2page()`
  - `btrfs_compress_str2level()`
  - `btrfs_compress_type2str()`
  - `btrfs_compress_is_valid_type()`
  - `btrfs_compress_heuristic()`
  - `btrfs_compress_bio()`

- Compressed I/O:
  - `btrfs_alloc_compressed_write()`
  - `btrfs_submit_compressed_write()`
  - `btrfs_submit_compressed_read()`

- Folio and workspace management:
  - `btrfs_alloc_compr_folio()`
  - `btrfs_free_compr_folio()`
  - `btrfs_get_workspace()`
  - `btrfs_put_workspace()`

- Algorithm hooks:
  - zlib, lzo, and zstd compress/decompress/workspace functions.

## Invariants

- Compressed extent size constants are page-aligned; enforced by static assertion.
- `compressed_bio::bbio` must remain last because allocation embeds the bio object.
- Header assumes callers use `btrfs_free_compr_folio()` for compressed folios added to compressed bios.
- Zstd has custom workspace-manager functions, unlike zlib/lzo/heuristic generic managers.
