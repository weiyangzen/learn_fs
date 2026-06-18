# File Research: sources/os/linux/linux/fs/direct-io.c

## Role

Implements the legacy blockdev direct I/O engine used by filesystems through `__blockdev_direct_IO()`. It maps user iterator pages to filesystem blocks, builds bios, submits I/O, handles async completion, and reconciles direct I/O with inode size, page cache invalidation, and truncate synchronization.

## Major Responsibilities

- Extracts and pins pages from an `iov_iter`.
- Calls filesystem `get_block_t` mapping callbacks.
- Builds bios from page sections and block mappings.
- Handles holes, newly allocated blocks, and sub-filesystem-block alignment.
- Supports synchronous and asynchronous direct I/O.
- Tracks bio completion and propagates I/O errors.
- Calls optional filesystem `dio_iodone_t` completion hook.
- Coordinates with inode direct-I/O counters.

## Core Structures

`struct dio_submit` is submission-only state:

- Current bio under construction.
- Block sizing and alignment factors.
- Current file block and final request block.
- Current mapping extent state.
- Deferred current page section.
- Page extraction queue state.
- Iterator pointer.

`struct dio` is shared with completion paths:

- Operation flags and bio operation type.
- Inode, iocb, i_size snapshot.
- End-I/O callback and private filesystem data.
- Page pinning mode.
- Bio completion lock, refcount, waiter, and completed bio list.
- Async state and completion work.
- Result and error state.
- Page buffer for extracted pages.

## Page Extraction

`dio_refill_pages()` uses `iov_iter_extract_pages()` to fetch up to `DIO_PAGES` pages.

For writes, if page extraction fails after filesystem blocks have already been mapped, it substitutes `ZERO_PAGE(0)` to consume mapped blocks and avoid stale data exposure. The original page error is saved in `dio->page_errors`.

`dio_pin_page()` and `dio_unpin_page()` handle additional page pin accounting when the iterator extraction will pin pages.

## Bio Submission and Completion

`dio_bio_alloc()` allocates a bio with the selected block device, operation flags, sector, and end_io callback.

Async bios use `dio_bio_end_aio()`, which may complete directly or defer completion to the superblock direct-I/O workqueue.

Sync bios use `dio_bio_end_io()`, which links completed bios onto `dio->bio_list` for process-context completion.

`dio_bio_complete()` records `-EAGAIN` for `REQ_NOWAIT` / `BLK_STS_AGAIN`, otherwise `-EIO`, then releases or dirties pages as needed.

`dio_await_completion()` waits for and processes all submitted bios.

`dio_bio_reap()` periodically reaps completed bios during large submissions to limit memory and pinned-page pressure.

## Completion Semantics

`dio_complete()`:

- Converts `-EIOCBQUEUED` to non-error for final accounting.
- Computes transferred bytes.
- Truncates short reads past sampled `i_size`.
- Suppresses `-EFAULT` if some I/O completed.
- Applies saved page errors and I/O errors.
- Calls filesystem `end_io` hook if present.
- Performs post-write cache invalidation when requested.
- Calls `inode_dio_end()`.
- For async I/O, updates `ki_pos`, runs `generic_write_sync()` for writes, and calls `ki_complete()`.
- Frees the `dio` object.

Async completion can be deferred for O_DSYNC writes or when page cache invalidation may need process context.

## Block Mapping

`get_more_blocks()` calls the filesystem `get_block()` callback with a filesystem-block range. It supports:

- Creating blocks for writes.
- Avoiding creation for DIO_SKIP_HOLES writes inside file size.
- Large mapped extents through `bh->b_size`.
- Filesystem-provided private completion data through `b_private`.
- Deferred completion requests through `buffer_defer_completion()`.

## Page Section Submission

`submit_page_section()` coalesces contiguous page sections before sending them into bios. It also handles task write accounting.

`dio_send_cur_page()` ensures logical and physical contiguity before adding a page section to a bio. It prevents logically non-contiguous ranges from being merged into one bio, which is important for filesystems such as btrfs.

`dio_bio_add_page()` adds the current page section and updates block and page-in-I/O counters.

## Holes and Partial Blocks

`do_direct_IO()` walks user pages and file blocks.

For holes:

- Reads zero-fill pages until EOF.
- Writes return `-ENOTBLK`, causing the caller to fall back to buffered I/O for the rest.

For newly allocated partial filesystem blocks:

- `dio_zero_block()` writes zeroes before or after the user data when the direct-I/O block size is smaller than filesystem block size.

New block mappings trigger `clean_bdev_aliases()` to remove stale block-device aliases.

## Public Entry Point

`__blockdev_direct_IO()` validates alignment, determines sync versus async mode, initializes `struct dio`, starts `inode_dio_begin()`, runs submission under a block plug, cleans up pages, releases read locking when applicable, waits or queues async completion, and returns either byte count/error or `-EIOCBQUEUED`.

Locking behavior depends on flags:

- With `DIO_LOCKING`, reads acquire and release `i_rwsem`; writes are expected to enter with it held.
- Without `DIO_LOCKING`, the filesystem must synchronize direct I/O versus truncates and other I/O.

## Important Invariants

- `inode_dio_begin()` / `inode_dio_end()` brackets submitted direct I/O.
- Async completion returns `-EIOCBQUEUED` only when completion will happen later.
- Direct writes extending file size are forced synchronous for simpler filesystems.
- Filesystems must not expose newly allocated uninitialized partial blocks.
- Bio completion refcount is protected by `bio_lock`, not atomic operations, to coordinate waiter wakeups.
- Page cache invalidation after direct writes happens after filesystem end_io conversion.

## Research Notes

This file is a dense compatibility engine for direct I/O over block mappings. The most error-prone areas are partial-block zeroing, page pin lifetime, async completion ordering, and fallback behavior for holes or alignment constraints.
