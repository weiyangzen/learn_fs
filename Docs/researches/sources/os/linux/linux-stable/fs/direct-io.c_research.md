# File Research: sources/os/linux/linux-stable/fs/direct-io.c

## Purpose

`direct-io.c` implements the legacy blockdev direct I/O helper `__blockdev_direct_IO()`, mapping user iter pages to filesystem blocks, constructing BIOs, submitting them, and completing synchronous or asynchronous direct reads/writes.

## Main Responsibilities

- Extracts and pins user pages from an `iov_iter`.
- Calls filesystem `get_block_t` to map file blocks to disk blocks.
- Builds BIOs from page sections while preserving logical contiguity requirements.
- Handles holes, short reads, partial-block alignment, and newly allocated block zeroing.
- Tracks in-flight BIOs and completion errors.
- Supports sync and async completion, including deferred completion workqueue use.
- Integrates with inode direct-I/O exclusion through `inode_dio_begin()` and `inode_dio_end()`.
- Performs post-direct-write page-cache invalidation and write sync handling.

## Core Data Structures

- `struct dio_submit`: submission-only cursor tracking current BIO, block size factors, block mapping cursor, deferred current page section, page queue, and iterator state.
- `struct dio`: shared submission/completion state, including inode, kiocb, op flags, async flags, BIO refcount, completion list, errors, result bytes, and embedded page array/work item.

## Key Control Flow

Entry:
- `__blockdev_direct_IO()` validates count, alignment, EOF reads, and locking mode.
- It determines whether I/O can be async; extending writes are forced sync to avoid exposing uninitialized blocks in simpler filesystems.
- It initializes DIO state, starts a block plug, and calls `do_direct_IO()`.

Mapping and submission:
- `dio_refill_pages()` batches extracted pages; on write page fault after blocks were mapped, it uses `ZERO_PAGE` to consume mapped blocks and avoid stale data exposure.
- `get_more_blocks()` calls the filesystem block mapper and records completion-private data.
- `do_direct_IO()` walks blocks and pages, handles holes, maps chunks, and calls `submit_page_section()`.
- `submit_page_section()` coalesces adjacent chunks on a page or sends the previous page section into BIO assembly.
- `dio_send_cur_page()` starts a new BIO or submits existing BIOs when logical/physical contiguity breaks.
- `dio_zero_block()` submits zero-page sections for partial newly allocated filesystem blocks.

Completion:
- Async BIOs complete through `dio_bio_end_aio()` and may queue `dio_aio_complete_work()`.
- Sync BIOs complete into `dio->bio_list`; `dio_await_completion()` reaps and processes them in process context.
- `dio_complete()` derives the return value, calls optional filesystem `end_io`, invalidates cache after writes, ends inode DIO, performs async write sync if needed, invokes kiocb completion, and frees state.

## Important Dependencies

- Filesystem `get_block_t` and optional `dio_iodone_t`.
- BIO and block layer APIs.
- Page pinning and `iov_iter_extract_pages()`.
- Inode direct-I/O counters and optional `DIO_LOCKING`.
- Page cache invalidation helpers for direct writes.
- Superblock `s_dio_done_wq` for deferred async completion.

## Edge Cases and Risks

- `-ENOTBLK` is used internally as a signal to stop direct write submission and let callers fall back to buffered I/O.
- Partial filesystem-block writes to newly allocated blocks require zeroing the unwritten portions on disk.
- Async extending writes are forced synchronous because size updates before I/O completion could expose uninitialized data.
- BIO coalescing must respect both physical adjacency and logical file-offset adjacency, especially for filesystems such as btrfs.
- AIO completion can race with submission; `dio_complete()` normalizes `-EIOCBQUEUED` in that path.
- Read holes are zero-filled up to aligned EOF; write holes may force fallback.
