# File Research: sources/os/linux/linux-stable/fs/f2fs/compress.c

## Purpose
Implements F2FS per-file compression support, including backend algorithm adapters, compression/decompression memory management, compressed-cluster writeback, compressed read completion, overwrite/truncate handling, compressed-page cache, and cache/slab initialization.

## Main Components
- `f2fs_compress_ops` abstracts backend init/destroy/compress/decompress/level validation.
- Supported conditional backends are LZO, LZ4/LZ4HC, ZSTD, and LZO-RLE.
- Page-array allocation uses a per-superblock slab for common cluster sizes and heap allocation for larger arrays.
- A mempool preallocates intermediate compressed pages, controlled by `num_compress_pages`.
- `f2fs_compress_pages()` vmaps raw cluster pages and compressed output pages, runs the backend, writes the compression header/checksum, zeros unused tail bytes, and drops unused compressed pages.
- `f2fs_decompress_cluster()` prepares decompression memory, validates compressed length, runs backend decompression, verifies optional checksum, marks corruption/fsck-needed state, and completes read IO.
- Cluster helpers compute cluster indexes, validate compressed cluster layout, count compressed/raw blocks, and decide when a cluster may be compressed.
- Overwrite handling reads and locks a full compressed cluster before partial modification so compressed data can be rewritten coherently.
- Partial truncate of a compressed cluster expands it through overwrite preparation, zeroes the truncated range, writes it back, updates page cache, and truncates block mappings.
- `f2fs_write_compressed_pages()` writes compressed output blocks out-of-place, updates node block addresses with `COMPRESS_ADDR` and `NEW_ADDR`, manages encryption bounce pages, compressed IO context, writeback state, dirty-page counts, and compressed block accounting.
- `f2fs_write_raw_pages()` is the fallback path for uncompressible clusters or raw overwrite of compressed clusters.
- Decompression contexts (`decompress_io_ctx`) hold raw pages, compressed pages, optional temporary pages, vmap buffers, refcounts, fs-verity state, and deferred free work.
- Read completion caches compressed pages when `COMPRESS_CACHE` is enabled and memory thresholds allow it.
- Compress cache uses a special `compress_inode` mapping keyed by physical block address and tagged with source inode number for invalidation.
- Init/destroy routines create CIC/DIC slab caches, per-superblock page-array cache, compression mempool, and optional compress inode.

## Important Behaviors
- Compression only proceeds for full, valid, non-atomic clusters when compression is needed and checkpoint state is healthy.
- Compression must save at least one page plus header space; otherwise it returns `-EAGAIN` and falls back to raw writes.
- Checksum mismatch marks the inode `FI_COMPRESS_CORRUPT` and sets `SBI_NEED_FSCK`.
- fs-verity verification is deferred to the fs-verity workqueue to avoid deadlocks with compressed metadata reads.
- Writeback completion waits for all compressed pages before ending writeback on the original raw cluster pages.

## Dependencies
Uses F2FS data/node/segment write paths, fscrypt, fsverity, folios, mempool, vm_map_ram, LZO/LZ4/ZSTD libraries, tracepoints, and F2FS mount/memory options.

## Research Notes
This file coordinates several fragile lifetimes: raw page locks, compressed mempool pages, encryption bounce pages, CIC/DIC contexts, and cached compressed folios. Error paths deliberately fall back to raw writes or defer cleanup to avoid IO-context deadlocks.
