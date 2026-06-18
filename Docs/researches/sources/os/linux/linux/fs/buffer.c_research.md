# File Research: sources/os/linux/linux/fs/buffer.c

## Purpose
Implements Linux buffer-head support for block-device buffer cache lookup, buffer-backed folio read/write paths, dirty/writeback state coordination, metadata-buffer fsync lists, buffer LRU caching, direct buffer I/O submission, invalidation, truncation helpers, and buffer-head allocation/accounting.

## Main Elements
- Basic buffer operations: `touch_buffer()`, `__lock_buffer()`, `unlock_buffer()`, `__wait_on_buffer()`, `bio_endio_bh()`, `end_buffer_read_sync()`, `bh_end_read()`, and `bh_end_write()`.
- Async folio I/O completion: `end_buffer_async_read()`, `bh_end_async_read()`, and `bh_end_async_write()` coordinate per-buffer completion with folio uptodate/writeback state; read completion can enqueue fscrypt decryption and fsverity verification work.
- Metadata buffer lists: `mmb_init()`, `mmb_mark_buffer_dirty()`, `mmb_sync()`, `mmb_fsync_noflush()`, `mmb_fsync()`, and `mmb_invalidate()` maintain per-mapping dependent metadata buffers for simple filesystems and fsync ordering.
- Block-device buffer cache lookup: `__find_get_block_slow()`, per-CPU `bh_lru`, `__find_get_block()`, `__find_get_block_nonatomic()`, `bdev_getblk()`, `__bread_gfp()`, and `__breadahead()`.
- Buffer creation and initialization: `folio_alloc_buffers()`, `alloc_page_buffers()`, `create_empty_buffers()`, `folio_set_bh()`, `grow_buffers()`, and block-device folio buffer initialization.
- Dirty and error propagation: `block_dirty_folio()`, `mark_buffer_dirty()`, `mark_buffer_write_io_error()`, `write_dirty_buffer()`, `__sync_dirty_buffer()`, and `sync_dirty_buffer()`.
- Buffer-backed write path: `__block_write_full_folio()`, `folio_zero_new_buffers()`, `__block_write_begin_int()`, `block_write_begin()`, `block_write_end()`, `generic_write_end()`, and `block_write_full_folio()`.
- Buffer-backed read and mapping helpers: `block_read_full_folio()`, `block_is_partially_uptodate()`, `generic_block_bmap()`, and `iomap_to_bh()`.
- Truncation and invalidation: `block_invalidate_folio()`, `clean_bdev_aliases()`, `block_truncate_page()`, `try_to_free_buffers()`, and `discard_buffer()`.
- mmap/extension helpers: `generic_cont_expand_simple()`, `cont_write_begin()`, and `block_page_mkwrite()`.
- Allocation/accounting: `alloc_buffer_head()`, `free_buffer_head()`, CPU hotplug cleanup, `buffer_heads_over_limit`, `buffer_init()`, and buffer read batching helpers.

## Dependencies And Integration
This is a core VFS/block-layer bridge used by buffer-head filesystems, block devices, FS-Cache-adjacent netfs code, and legacy metadata paths. It integrates with folios and address spaces, writeback control, bios and blk-crypto, fscrypt, fsverity, cgroup writeback accounting, block-device mappings, per-CPU CPU hotplug state, and filesystem `get_block_t` callbacks.

## Risk Notes
Correctness depends on careful synchronization between folio locks, `i_private_lock`, buffer lock bits, folio dirty/writeback flags, and per-buffer state. Partial-block writes, truncate races, device-size races, blockdev alias invalidation, and fscrypt/fsverity completion failure paths are high-risk. Buffer LRU references can interfere with migration, so isolated CPUs and disabled LRU states are explicitly handled.
