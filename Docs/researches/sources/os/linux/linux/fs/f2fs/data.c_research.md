# File Research: sources/os/linux/linux/fs/f2fs/data.c

## Summary
Implements F2FS data I/O, block mapping, read/write folio operations, writeback, direct-I/O iomap mapping, fiemap, swapfile activation, and BIO lifecycle handling. It is the main bridge between the F2FS logical block tree, page cache folios, compression/encryption/verity post-processing, and block-device BIO submission.

## Main Responsibilities
- Allocates, merges, submits, and completes read/write BIOs.
- Handles post-read decrypt, decompress, and fs-verity verification steps.
- Maps logical file blocks to physical blocks for buffered I/O, DIO, bmap, fiemap, precache, and allocation paths.
- Reads normal, compressed, inline, and large folio data.
- Writes data pages through in-place update or out-of-place update policies.
- Implements `address_space_operations` for data files.
- Supports swapfile activation by validating and migrating extents to section-aligned pinned blocks.
- Initializes/destroys BIO, post-read, and large-folio state caches.

## Key APIs
- BIO/cache lifecycle: `f2fs_init_bioset()`, `f2fs_destroy_bioset()`, `f2fs_init_post_read_processing()`, `f2fs_init_bio_entry_cache()`.
- Submission: `f2fs_submit_page_bio()`, `f2fs_submit_page_write()`, `f2fs_submit_read_bio()`, `f2fs_submit_merged_write()`, `f2fs_flush_merged_writes()`.
- Mapping/allocation: `f2fs_map_blocks()`, `f2fs_get_block_locked()`, `f2fs_reserve_block()`, `f2fs_update_data_blkaddr()`.
- Reads: `f2fs_get_read_data_folio()`, `f2fs_find_data_folio()`, `f2fs_get_lock_data_folio()`, `f2fs_get_new_data_folio()`.
- Writeback: `f2fs_do_write_data_page()`, `f2fs_write_single_data_page()`, `f2fs_write_data_pages()`, `f2fs_write_failed()`.
- Exported operations: `f2fs_dblock_aops`, `f2fs_iomap_ops`.

## Important Behavior
Read completion calls `f2fs_finish_read_bio()`, which updates page accounting, handles compressed page completion, validates node-page footers, and ends folio reads. Reads may be routed through `f2fs_post_read_work()` for fscrypt decryption and compressed cluster decompression, then through fs-verity verification work.

Write completion handles fscrypt bounce folios, compressed write completion, checkpoint failure escalation for CP data, node footer sanity checks, fsync node list cleanup, page-count accounting, and writeback completion.

`f2fs_map_blocks()` is the central logical-to-physical mapper. It consults the read extent cache, walks dnodes, validates block addresses, optionally reserves or allocates blocks, handles holes/`NEW_ADDR`/`COMPRESS_ADDR`, updates read extent cache during precache, supports multi-device DIO translation, and waits on writeback for direct I/O mappings.

Buffered reads use `f2fs_mpage_readpages()` and `f2fs_read_single_page()`, with special paths for inline data, compressed clusters, fs-verity, readahead, and immutable large folios. Compressed reads assemble cluster state and read compressed pages into a decompression context rather than marking pagecache pages directly up-to-date per BIO.

Writeback uses a customized `write_cache_pages` loop to handle hot/cold data policy, compression clusters, sync-vs-async write serialization, dirty folio collection, retry on checkpoint races, merged BIO submission, and IPU BIO flushing.

`f2fs_write_begin()` reserves or finds blocks, converts inline data when needed, handles atomic-file COW inode writes, prepares compressed overwrites, waits for writeback, and reads partial existing data unless the block is newly allocated. `f2fs_write_end()` marks folios dirty, updates atomic flags and file size, and delegates compressed overwrite completion.

## State and Synchronization
Uses per-type write merge state in `sbi->write_io`, per-BIO post-read contexts from a mempool, BIO entry slabs for IPU write tracking, and per-large-folio `f2fs_folio_state` for partial read completion. Synchronization includes F2FS operation locks, dnode/node folio writeback waits, BIO list locks, writepage serialization mutexes, checkpoint/writeback counters, folio locks, invalidate locks, and zoned-device completions.

## Risks
The file has many paths where block-address validity, dnode lifetime, and page-cache state must agree. Compression, encryption, fs-verity, atomic COW writes, multi-device DIO, zoned devices, and checkpoint-disabled modes all alter normal I/O behavior. Incorrect lock ordering around folio locks, node locks, and `f2fs_lock_op()` can deadlock. Extent-cache hits must still honor writeback waits and device translation. Large folio read accounting depends on `read_pages_pending` being incremented before BIO submission and decremented exactly once per completed subpage.
