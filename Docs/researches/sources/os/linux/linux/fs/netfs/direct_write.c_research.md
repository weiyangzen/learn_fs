# File Research: sources/os/linux/linux/fs/netfs/direct_write.c

## Role

Unbuffered/direct write support for netfs users. It writes directly to the server, bypassing pagecache and local cache, while serializing subrequests to avoid gaps after partial failures, coordinating with direct-I/O counters, invalidating cached folios, and supporting async `kiocb` completion.

## Completion and Collection

- `netfs_unbuffered_write_done()` finalizes a write request:
  - updates inode size if no request error occurred;
  - invalidates pagecache folios covering direct-write ranges that may have appeared via mmap;
  - calls `inode_dio_end()` for direct writes;
  - wakes waiters on `NETFS_RREQ_IN_PROGRESS`;
  - advances async `ki_pos` and calls `ki_complete()`;
  - clears subrequests.
- `netfs_unbuffered_write_collect()` removes a completed subrequest from its stream, advances transferred counts and request iterator, updates collected offsets, and drops the subrequest reference.

## Direct Write Engine

`netfs_unbuffered_write()`:

- begins direct-I/O accounting for `NETFS_DIO_WRITE`;
- prepares one subrequest at a time through `netfs_prepare_write()`;
- truncates the iterator to remaining request length and stream limits;
- submits via `stream->issue_write()`;
- waits for each subrequest before dispatching the next to prevent unwritten holes after errors such as `ENOSPC`;
- records failures in `wreq->error`;
- handles retry requests by advancing past transferred bytes, invoking optional filesystem `retry_request()`, resetting subrequest flags/iterator/start/length, and reissuing;
- finalizes through `netfs_unbuffered_write_done()`.

## Public Entry Points

- `netfs_unbuffered_write_iter_locked()`
  - Creates a write request for `NETFS_DIO_WRITE` or `NETFS_UNBUFFERED_WRITE`.
  - Extracts user-backed iterators into request-owned bvec storage, recording pin/unpin state, or copies stable kernel iterators.
  - Sets `NETFS_RREQ_USE_IO_ITER` and `NETFS_RREQ_UPLOAD_TO_SERVER`.
  - Queues async writes on `system_dfl_wq` and returns `-EIOCBQUEUED`, or runs synchronously and advances `ki_pos`.
- `netfs_unbuffered_write_iter()`
  - Returns 0 for empty writes.
  - Brackets operation with `netfs_start_io_direct()` / `netfs_end_io_direct()`.
  - Runs generic write checks, privilege stripping, and time update.
  - For `IOCB_NOWAIT`, refuses to block if cached pages exist or invalidation would block.
  - Otherwise waits for dirty pagecache in range.
  - Invalidates clean cached pages before issuing the direct write.
  - Updates the netfs zero point under `inode->i_lock`.
  - Invalidates the FS-Cache cookie for the direct-write range.
  - Calls the locked direct write helper.

## Dependencies

Uses netfs write request creation, write preparation/issue/retry helpers, iterator extraction, direct-I/O counters, pagecache invalidation/writeback, FS-Cache invalidation, inode size/zero-point helpers, and async workqueue completion.

## Research Notes

The important correctness choice is serial subrequest dispatch. Unlike reads, direct writes are not freely parallelized because a later successful subrequest after an earlier partial failure could create server-side holes. Pagecache and FS-Cache are invalidated before direct writes so later buffered reads refetch authoritative data.
