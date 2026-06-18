# File Research: sources/os/linux/linux-stable/fs/netfs/direct_read.c

## Purpose

`direct_read.c` implements netfs direct and unbuffered read support. It bypasses pagecache and local disk cache, slices application-buffer reads into subrequests according to netfs/server limits, and supports synchronous and asynchronous kiocb completion.

## Main Entry Points

- `netfs_unbuffered_read_iter_locked(struct kiocb *iocb, struct iov_iter *iter)`
  - Performs direct or unbuffered read when caller already holds appropriate locks.

- `netfs_unbuffered_read_iter(struct kiocb *iocb, struct iov_iter *iter)`
  - Public wrapper that serializes direct I/O using `netfs_start_io_direct()` / `netfs_end_io_direct()`.

Internal helpers:

- `netfs_unbuffered_read()`
- `netfs_dispatch_unbuffered_reads()`
- `netfs_prepare_dio_read_iterator()`

## Read Dispatch Flow

`netfs_unbuffered_read_iter_locked()`:

1. Returns 0 for empty read without updating atime.
2. Calls `kiocb_write_and_wait()` to flush conflicting writes.
3. Updates file access time.
4. Allocates `netfs_io_request` with origin:
   - `NETFS_DIO_READ` for `IOCB_DIRECT`
   - `NETFS_UNBUFFERED_READ` otherwise
5. Extracts or copies the destination iterator:
   - User-backed iterators are extracted into a bvec iterator with `netfs_extract_user_iter()`.
   - Non-user-backed iterators are copied directly and advanced.
6. For async operations, stores `iocb` and sets `NETFS_RREQ_OFFLOAD_COLLECTION`.
7. Calls `netfs_unbuffered_read()`.

`netfs_unbuffered_read()`:

- Rejects zero-sized request as `-EIO`.
- Begins inode DIO accounting with `inode_dio_begin()`.
- Dispatches subrequests.
- Waits synchronously or returns `-EIOCBQUEUED` for async.

## Subrequest Slicing

`netfs_dispatch_unbuffered_reads()` loops over the requested range:

- Allocates a subrequest.
- Sets source to `NETFS_DOWNLOAD_FROM_SERVER`.
- Sets start and length.
- Queues it with `netfs_queue_read()`.
- Runs filesystem `prepare_read()` if present.
- Calls `netfs_prepare_dio_read_iterator()` to limit and assign iterator.
- Updates request submitted count.
- Sets `NETFS_RREQ_ALL_QUEUED` when final slice is queued.
- Calls filesystem `issue_read()`.
- Honors pause and failed flags.

If allocation or preparation fails while bytes remain, it sets `NETFS_RREQ_ALL_QUEUED` and wakes the collector so outstanding state can complete.

`netfs_prepare_dio_read_iterator()`:

- Limits length to stream `sreq_max_len`.
- Applies segment count limits via `netfs_limit_iter()`.
- Assigns `subreq->io_iter` from request iterator.
- Truncates subrequest iterator and advances request iterator.

## Iterator Ownership

The direct read path must preserve user buffers across async completion:

- User-backed iterators are extracted into request-owned bvecs.
- `direct_bv`, `direct_bv_count`, and `direct_bv_unpin` track extracted buffers and pinning behavior.
- Non-user-backed iterators are assumed stable for the operation.

## Completion Semantics

- Sync reads wait via `netfs_wait_for_read()`, advance `iocb->ki_pos`, and return transferred bytes.
- Async reads return `-EIOCBQUEUED`; completion is handled by the netfs read collector.
- `inode_dio_end()` is intentionally left to collection because subrequests may still be outstanding.

## Exports

Exports:

- `netfs_unbuffered_read_iter_locked`
- `netfs_unbuffered_read_iter`

## Key Takeaways

This file is a thin but critical direct-read adapter: it turns a user/kernel iterator into request-owned I/O state, slices by netfs limits, bypasses cache/pagecache, and hands completion to netfs read collection.
