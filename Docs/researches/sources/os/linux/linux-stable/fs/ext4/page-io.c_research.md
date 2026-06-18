# File Research: sources/os/linux/linux-stable/fs/ext4/page-io.c

## Summary
Implements ext4 buffered writeback bio submission and completion. It manages `ext4_io_end` lifetimes, encrypted bounce folios, buffer-head writeback completion, unwritten extent conversion, deferred completion work, and writeback bio construction.

## Main Responsibilities
- Initialize and destroy slab caches for `ext4_io_end` and `ext4_io_end_vec`.
- Allocate/free unwritten extent conversion vectors attached to writeback completions.
- Finish write bios by clearing buffer async-write state, recording I/O errors, freeing encryption bounce pages, and ending folio writeback.
- Convert successfully written unwritten extents to written extents.
- Abort the journal on configured data writeback errors.
- Defer completion when unwritten conversion or journal-abort work cannot be completed in bio end I/O context.
- Build and submit write bios with fscrypt contexts and writeback accounting.
- Write a folio’s mapped dirty buffers while preserving dirty state for buffers not eligible for writeout.

## Key Data Structures
- `ext4_io_end_t`: per-writeback completion object with inode, bio chain, flags, handle, refcount, and conversion vectors.
- `struct ext4_io_end_vec`: records ranges needing unwritten extent conversion.
- `struct ext4_io_submit`: per-writeback bio aggregation state: current bio, next physical block, writeback control, and current io_end.

## Key Functions
- `ext4_init_pageio()` / `ext4_exit_pageio()`: manage writeback completion caches.
- `ext4_alloc_io_end_vec()`, `ext4_last_io_end_vec()`, `ext4_free_io_end_vec()`: manage conversion vector list lifetime.
- `ext4_finish_bio()`: walks all folios in a completed bio, maps bounce folios back to page-cache folios, marks buffer errors, clears async-write bits, and ends folio writeback when no buffers remain under I/O.
- `ext4_release_io_end()`: finishes all bios chained on an io_end, releases vectors, and frees the io_end.
- `ext4_end_io_end()`: handles final completion; skips unwritten conversion on writeback failure, frees reserved handles or converts unwritten extents, reports potential data loss on conversion failure, and releases the io_end.
- `ext4_io_end_defer_completion()` and `ext4_add_complete_io()`: decide and queue deferred completion work.
- `ext4_do_flush_completed_IO()` and `ext4_end_io_rsv_work()`: drain deferred per-inode conversion/error-completion lists.
- `ext4_init_io_end()`, `ext4_get_io_end()`, `ext4_put_io_end()`, `ext4_put_io_end_defer()`: reference-counted io_end lifecycle helpers.
- `ext4_end_bio()`: write bio completion handler; records errors, chains bios for deferred completion, or directly finishes buffers.
- `ext4_io_submit()` / `ext4_io_submit_init()`: submit accumulated bios and initialize submission state.
- `io_submit_init_bio()`, `io_submit_need_new_bio()`, `io_submit_add_bh()`: allocate, merge, and fill write bios.
- `ext4_bio_write_folio()`: prepares a locked folio for writeback, marks eligible buffers async-write, encrypts into bounce pages if needed, starts writeback, and submits each buffer to bios.

## Writeback Semantics
`ext4_bio_write_folio()` writes only dirty, mapped, non-delayed, non-unwritten buffers. Holes can have dirty state cleared, while dirty buffers that cannot yet be written are redirtied and may retain TOWRITE so synchronous writeback does not skip them. Partial EOF folios are zeroed beyond valid file length before writeout.

## Error Handling
Write bio errors set mapping errors, set buffer write I/O error state, emit compatible buffer I/O messages, and set `EXT4_IO_END_FAILED`. If `DATA_ERR_ABORT` is enabled and the filesystem is not already in emergency state, failed deferred completion can abort the journal. Unwritten extents are not converted after failed data writeback to avoid exposing stale data.

## Synchronization and Lifetime
- `i_completed_io_lock` protects each inode’s deferred completion list.
- io_end refcounts prevent early release while bios are in flight.
- Multiple bio completions can race; completed bios are chained with `xchg(&io_end->bio, bio)`.
- Buffer async-write state is cleared under `b_uptodate_lock`.
- Bounce pages are freed only after associated page-cache folio writeback is complete.

## Dependencies
Depends on buffer heads, folios, writeback control, bios, block crypto, fscrypt pagecache encryption, jbd2 reserved handles, ext4 unwritten extent conversion, and ext4 per-inode deferred conversion workqueues.

## Risks and Edge Cases
- Unwritten extent conversion failure after successful I/O is treated as potential data loss and reported at emergency level.
- Encryption bounce page allocation has careful retry behavior to avoid mempool deadlocks.
- Folio writeback must not end until all async-write buffers in that folio have completed.
- Deferred completion requires a valid reserved handle for unwritten conversion when journaling is active.
