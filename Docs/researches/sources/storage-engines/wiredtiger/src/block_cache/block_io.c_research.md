# sources/storage-engines/wiredtiger/src/block_cache/block_io.c

## Purpose

`block_io.c` is the high-level block I/O adapter between B-tree pages and `WT_BM` physical managers. It performs mapped reads, block-cache reads, multi-read delta handling, compression, decompression, encryption, decryption, checksum policy selection, statistics, corruption escalation, and block-cache write allocation.

## Important APIs, Types, and Functions

Public functions are `__wt_blkcache_read`, `__wt_blkcache_read_multi`, `__wt_blkcache_compress`, and `__wt_blkcache_write`. Important private helpers are `__blkcache_read_corrupt`, `__blkcache_read_decrypt`, `__blkcache_cache_wants_encrypted_data`, and `__read_decompress`. It uses `WT_BM`, `WT_BTREE`, `WT_BLKCACHE_ITEM`, `WT_PAGE_BLOCK_META`, `WT_PAGE_HEADER`, `WT_BLOCK_DISAGG_HEADER`, compressors, encryptors, and delta arrays.

## Control Flow

Single-read first chooses a scratch buffer when conversion is expected, tries memory mapping, then block cache, then `bm->read` or `bm->read_multiple`. Disk reads update page-type and cache-read stats before conversion. It rejects unencrypted disk blocks when encryption is configured, optionally decrypts, inserts an encrypted or decrypted image into block cache depending on cache type, decompresses if needed, copies into the caller buffer, and physically verifies pages when the btree is in verify mode.

Multi-read returns base plus deltas. If the physical manager lacks `read_multiple`, it falls back to single-read with one result. Otherwise it can fetch cached base/deltas, or call the manager, decrypt/decompress the base image, then decrypt/decompress each delta using disaggregated block-header flags. Results are returned as an allocated `WT_ITEM` array.

Writes compress when configured and beneficial, encrypt when configured, derive data-checksum policy from the btree checksum mode, call either checkpoint or normal `WT_BM` write, update cache/write statistics, and optionally insert written page images into the block cache unless disabled, checkpoint-bypassed, no-write-allocate, final-checkpoint, or delta-bearing.

## State and Persistence Behavior

This layer persists data indirectly through `WT_BM.write`/`checkpoint`, and it mutates runtime caches, stats, scratch buffers, returned `WT_ITEM` ownership, and page flags (`WT_PAGE_COMPRESSED`, `WT_PAGE_ENCRYPTED`). It can store encrypted images in NVRAM cache and decrypted images in DRAM cache. It does not itself own file allocation state.

## Dependencies and Integration Points

The file integrates compressors, encryptors, block cache, block mapping, disaggregated multi-block reads, physical `WT_BM` methods, verification, WiredTiger cache/session stats, and corruption handling that calls `bm->corrupt` then panics outside verify/quiet-corrupt mode.

## Risks and Edge Cases

Buffer ownership in multi-read is subtle: cached data is borrowed until ref-count release, while disk-read results are freed or moved into the returned array. Compression ratio calculations divide by compressed lengths and assume meaningful sizes. Decompression passes `tmp->size` in the single-read path, so scratch-buffer state must match the source image. Deltas are cached but write-side block-cache insertion currently ignores delta-bearing writes. Encryption skip size depends on the block-manager method.

## Test Signals

Tests should cover compressed and encrypted read/write combinations, missing compressor/decryptor corruption, unencrypted disk data with configured encryption, mapped-read bypass, block-cache hit with conversion, multi-read base plus deltas, checksum policy modes, cache-on-checkpoint/cache-on-writes bypass stats, and verify-mode physical page validation.
