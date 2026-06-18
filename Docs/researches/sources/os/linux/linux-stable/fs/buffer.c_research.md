# File Research: sources/os/linux/linux-stable/fs/buffer.c

This is the Linux buffer-head implementation for block-buffer-backed address spaces. It provides core primitives used by block devices and legacy or buffer-head-based filesystems for block lookup, buffer allocation, dirty tracking, read/write submission, folio integration, invalidation, and fsync support.

Major responsibilities:
- Buffer locking and completion: `__lock_buffer()`, `unlock_buffer()`, `__wait_on_buffer()`, `end_buffer_read_sync()`, `end_buffer_write_sync()`, async read/write completion handlers, and error propagation through `mark_buffer_write_io_error()`.
- Buffer cache lookup and allocation: per-CPU `bh_lru`, `__find_get_block()`, `__find_get_block_nonatomic()`, `bdev_getblk()`, `__bread_gfp()`, `__breadahead()`, `grow_buffers()`, and block-device folio buffer initialization.
- Folio and buffer state coherence: `block_dirty_folio()`, `create_empty_buffers()`, `folio_alloc_buffers()`, `try_to_free_buffers()`, `block_invalidate_folio()`, `clean_bdev_aliases()`, and dirty/writeback checks.
- Generic buffered write path: `__block_write_full_folio()`, `block_write_full_folio()`, `__block_write_begin_int()`, `block_write_begin()`, `block_write_end()`, `generic_write_end()`, and zeroing helpers.
- Generic buffered read path: `block_read_full_folio()` maps blocks, submits async reads, zero-fills holes, integrates fscrypt decryption and fsverity verification.
- Truncation and mmap write support: `block_truncate_page()` and `block_page_mkwrite()`.
- Direct buffer I/O submission: `submit_bh_wbc()`, `submit_bh()`, `write_dirty_buffer()`, `__sync_dirty_buffer()`, `sync_dirty_buffer()`, `__bh_read()`, and `__bh_read_batch()`.
- Metadata buffer fsync helper support: `mapping_metadata_bhs` management through `mmb_init()`, `mmb_mark_buffer_dirty()`, `mmb_sync()`, `mmb_fsync_noflush()`, `mmb_fsync()`, and `mmb_invalidate()`.

Important design points:
- The file is built around `struct buffer_head` rings attached to folios via `b_this_page`, with the folio private pointer storing the ring head.
- Dirty state is deliberately duplicated between folios and buffers. The code carefully orders dirtying and cleaning to avoid dirty buffer / clean folio inconsistencies.
- Block-device buffer cache lookup is accelerated with a per-CPU 16-entry LRU. It disables local IRQs or preemption while manipulating LRU entries and avoids isolated CPUs.
- `i_private_lock` protects buffer attachment/removal against `block_dirty_folio()` and `try_to_free_buffers()`. Folio locks are used where sleeping is possible and scale better than a mapping-global spinlock.
- The async read path can enqueue fscrypt decryption and fsverity verification work before completing the folio read.
- Writes use buffer-level dirty bits to decide which blocks to submit, then use folio writeback state to protect the buffer ring during submission.
- I/O errors are surfaced to the address-space error state and, for metadata lists, to the metadata mapping as well.

Key invariants:
- `submit_bh_wbc()` requires the buffer to be locked, mapped, have an end I/O handler, and not be delayed or unwritten.
- `try_to_free_buffers()` requires a locked folio and refuses to free buffers under writeback or with dirty/locked/refcounted buffer heads.
- `block_invalidate_folio()` requires a locked folio and clears mapped-to-disk state after invalidating affected buffers.
- Block write begin handles all mapped/uptodate combinations, with holes zero-filled and newly allocated partial blocks zeroed to avoid stale data exposure.
- Buffer-head allocation is accounted per CPU, with `buffer_heads_over_limit` set when live buffer heads exceed the computed limit.

External interfaces exported here are broad and central to filesystem code: buffer allocation/free, block lookup/read helpers, folio dirtying/invalidation, generic block read/write helpers, truncate/mkwrite helpers, bio submission wrappers, and fsync metadata helpers.
