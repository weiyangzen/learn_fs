# File Research: sources/os/linux/linux/fs/ext4/page-io.c

## Purpose
Implements ext4 page-cache writeback BIO submission and completion, including `ext4_io_end` lifetime management, encrypted bounce-page handling, writeback buffer status, unwritten extent conversion, and deferred completion work.

## Main Entry Points
- `ext4_init_pageio()` / `ext4_exit_pageio()` manage slab caches for `ext4_io_end` and vector records.
- `ext4_init_io_end()`, `ext4_get_io_end()`, `ext4_put_io_end()`, and `ext4_put_io_end_defer()` manage I/O-end references.
- `ext4_io_submit_init()` / `ext4_io_submit()` prepare and submit write BIOs.
- `ext4_bio_write_folio()` turns a dirty mapped folio into one or more BIO segments.
- `ext4_end_io_rsv_work()` flushes deferred unwritten-extent conversions.

## Writeback Flow
`ext4_bio_write_folio()` zeros beyond EOF, scans buffers to select dirty mapped non-delayed written buffers, clears `buffer_new`, marks `buffer_async_write`, clears dirty bits, and starts folio writeback. If nothing can be submitted, it cycles writeback state and preserves dirty/TOWRITE state for buffers still blocked by journal state. For fs-layer encrypted files, it encrypts page-cache blocks into a bounce page, retrying with stronger GFP constraints when necessary.

BIO setup groups contiguous blocks with compatible encryption context. `io_submit_add_bh()` submits and starts new BIOs when physical contiguity or crypto mergeability breaks. `ext4_io_submit()` applies `REQ_SYNC` for synchronous writeback and submits via `blk_crypto_submit_bio()`.

## Completion Flow
`ext4_end_bio()` records write errors, marks `EXT4_IO_END_FAILED`, and either defers completion or finishes the BIO immediately. `ext4_finish_bio()` walks BIO folios, maps bounce folios back to page-cache folios, sets mapping errors, clears async-write bits under the buffer lock, reports buffer I/O errors, frees bounce pages, and ends folio writeback when no buffers remain under I/O.

If completion must convert unwritten extents or abort on data errors, `ext4_add_complete_io()` queues the inode’s reserved-conversion work. `ext4_end_io_end()` either frees a reserved journal handle on failed I/O or calls `ext4_convert_unwritten_io_end_vec()`, then releases the `io_end`.

## Integration Points
Interacts with buffer heads, folios, writeback control, blk-crypto, fscrypt, JBD2 reserved handles, ext4 unwritten extent conversion, inode per-I/O lists, and the mount option `DATA_ERR_ABORT`.

## Invariants and Risks
A folio cannot finish writeback until all async-write buffers covered by pending BIOs are complete. Deferred completion must hold enough state to safely convert unwritten extents after I/O. On write failure, unwritten conversion is skipped to avoid exposing stale data, and the journal may be aborted if configured.

## Testing Signals
Cover encrypted writeback bounce-page allocation failure, noncontiguous BIO splitting, partial EOF folio zeroing, delayed/unwritten buffer redirty paths, write I/O errors with `DATA_ERR_ABORT`, and successful/failed unwritten extent conversion.
