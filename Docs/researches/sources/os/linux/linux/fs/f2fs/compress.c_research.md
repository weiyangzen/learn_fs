# File Research: sources/os/linux/linux/fs/f2fs/compress.c

## Purpose
Implements F2FS compression and decompression support, including backend dispatch, cluster compression, compressed writeback, compressed read completion, overwrite/truncate handling, cache support, and slab/mempool lifecycle.

## Main Responsibilities
- Provides backend abstraction through `struct f2fs_compress_ops`.
- Supports LZO, LZO-RLE, LZ4/LZ4HC, and ZSTD depending on Kconfig.
- Allocates intermediate compressed pages from a mempool and per-mount page-array slabs.
- Compresses full clusters and writes them as `COMPRESS_ADDR` header plus compressed data blocks.
- Decompresses read clusters, verifies optional compression checksums, and integrates with fsverity.
- Falls back to raw page writeback when compression is unsuitable or not beneficial.
- Maintains optional compressed-page cache through a special compress inode mapping.

## Key Functions and Flows
- Context setup: `f2fs_init_compress_ctx()`, `f2fs_destroy_compress_ctx()`, and `f2fs_compress_ctx_add_page()`.
- Backend readiness and levels: `f2fs_is_compress_backend_ready()` and `f2fs_is_compress_level_valid()`.
- Compression: `f2fs_compress_pages()` vmaps raw and compressed pages, calls backend compression, writes header/checksum/reserved fields, zeroes tail bytes, and trims unused cpages.
- Writeback: `f2fs_write_multi_pages()` tries compression for eligible full clusters, otherwise falls back to `f2fs_write_raw_pages()`.
- Compressed write: `f2fs_write_compressed_pages()` updates node block addresses, invalidates replaced blocks, handles encryption bounce pages, submits out-of-place writes, updates compressed-block accounting, and completes via `f2fs_compress_write_end_io()`.
- Decompression: `f2fs_alloc_dic()` prepares decompress context and pages; `f2fs_end_read_compressed_page()` triggers `f2fs_decompress_cluster()` after all compressed pages complete; `f2fs_decompress_end_io()` marks/unlocks output pages or schedules fsverity verification.
- Overwrite/truncate: `f2fs_prepare_compress_overwrite()` reads and locks an existing compressed cluster before modification; `f2fs_truncate_partial_cluster()` zeroes partial cluster tails and rewrites safely.
- Cache: `f2fs_cache_compressed_page()`, `f2fs_load_compressed_folio()`, and invalidation helpers cache compressed disk pages by block address when `COMPRESS_CACHE` is enabled.

## Edge Cases
- Compression is skipped for atomic files, incomplete clusters, invalid data beyond EOF, checkpoint-error filesystems, and low-benefit results.
- Decompression checks compressed length bounds and optional checksum; checksum mismatch marks the inode corrupt and sets `SBI_NEED_FSCK`.
- fsverity verification is moved to the fsverity workqueue to avoid decompression workqueue deadlocks.
- Quota inode compressed writeback uses `node_write` locking to avoid checkpoint allocation races.
