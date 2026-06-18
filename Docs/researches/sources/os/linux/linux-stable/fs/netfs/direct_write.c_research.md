# File Research: sources/os/linux/linux-stable/fs/netfs/direct_write.c

## Purpose

`direct_write.c` implements netfs unbuffered and direct write support. It writes data directly to the server without going through pagecache or local FS-Cache, while coordinating direct I/O exclusion, cache invalidation, i_size update, retry, and async kiocb completion.

## Main Entry Points

- `netfs_unbuffered_write_iter_locked(struct kiocb *iocb, struct iov_iter *iter, struct netfs_group *netfs_group)`
  - Creates and dispatches an unbuffered/direct write request when caller holds appropriate locks.

- `netfs_unbuffered_write_iter(struct kiocb *iocb, struct iov_iter *from)`
  - Public write path with generic checks, direct I/O serialization, pagecache invalidation, zero-point update, and cache invalidation.

Internal helpers:

- `netfs_unbuffered_write()`
- `netfs_unbuffered_write_collect()`
- `netfs_unbuffered_write_done()`
- `netfs_unbuffered_write_async()`

## Public Write Flow

`netfs_unbuffered_write_iter()`:

1. Returns 0 on empty write.
2. Traces and counts DIO write stats.
3. Starts direct I/O serialization with `netfs_start_io_direct()`.
4. Runs `generic_write_checks()`.
5. Removes privileges and updates timestamps.
6. Handles `IOCB_NOWAIT` by rejecting if range has pagecache pages that would block invalidation.
7. Otherwise writes and waits for pagecache data in range.
8. Invalidates clean cached pages in the write range before direct write.
9. Updates netfs zero point under `inode->i_lock` if write extends it.
10. Invalidates FS-Cache cookie with `FSCACHE_INVAL_DIO_WRITE`.
11. Calls locked unbuffered write helper.
12. Ends direct I/O serialization.

## Request Setup

`netfs_unbuffered_write_iter_locked()`:

- Creates a write request using `netfs_create_write_req()`.
- Origin is `NETFS_DIO_WRITE` for `IOCB_DIRECT`, otherwise `NETFS_UNBUFFERED_WRITE`.
- Marks stream 0 available.
- Extracts user-backed iterators into request-owned bvecs with `netfs_extract_user_iter()`.
- Copies non-user iterators directly.
- Sets `NETFS_RREQ_USE_IO_ITER` and `NETFS_RREQ_UPLOAD_TO_SERVER`.
- For async writes, queues work to `system_dfl_wq` and returns `-EIOCBQUEUED`.
- For sync writes, calls `netfs_unbuffered_write()` and returns transferred bytes or error.

The file has TODO placeholders for bounce-buffer encryption/compression style transforms.

## Serial Subrequest Dispatch

`netfs_unbuffered_write()` intentionally dispatches subrequests serially:

- It prepares a write subrequest through `netfs_prepare_write()`.
- Truncates iterator to remaining request length.
- Limits request by stream max length and max segments.
- Issues write with `stream->issue_write()`.
- Waits for stream progress before issuing the next subrequest.

The serial design avoids gaps on partial failures such as server-side `ENOSPC`.

## Retry Handling

If a subrequest needs retry:

- Marks subrequest error `-EAGAIN`.
- Advances request iterator by bytes already transferred.
- Calls filesystem `retry_request()` if available for server uploads.
- Clears retry/boundary/failed flags.
- Resets iterator, start, len, transferred, and increments retry count.
- Resets max length/segments.
- Either re-runs stream `prepare_write()` or reissues with `netfs_reissue_write()`.

## Completion And Cleanup

`netfs_unbuffered_write_collect()`:

- Removes subrequest from stream list.
- Adds transferred bytes to request.
- Advances request iterator.
- Updates stream/request collected positions.
- Drops subrequest ref.

`netfs_unbuffered_write_done()`:

- Updates inode size if no request error.
- For DIO writes, invalidates any pagecache folios that mmap may have populated under the written range.
- Calls `inode_dio_end()` for DIO writes.
- Wakes waiters on `NETFS_RREQ_IN_PROGRESS`.
- Completes async kiocb by advancing `ki_pos` and calling `ki_complete()`.
- Clears subrequests.

## Error Handling

- Failed preparation stores subrequest error into request and exits.
- Failed issued write records `wreq->error`.
- Signal during synchronous non-kiocb write returns `-EINTR` after progress or `-ERESTARTSYS` before progress.
- Sync caller returns transferred bytes if any, otherwise error.
- Async caller returns `-EIOCBQUEUED`.

## Exports

Exports:

- `netfs_unbuffered_write_iter_locked`
- `netfs_unbuffered_write_iter`

## Key Takeaways

This file is the direct/unbuffered write counterpart to the buffered write machinery. It prioritizes contiguous server writes, direct I/O accounting, pagecache/cache coherency, and safe async completion over parallel subrequest dispatch.
