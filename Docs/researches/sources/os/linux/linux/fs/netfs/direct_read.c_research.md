# File Research: sources/os/linux/linux/fs/netfs/direct_read.c

## Role

Unbuffered/direct read support for netfs users. It bypasses pagecache and local cache, slices reads according to network limits, pins or copies caller iterators as needed for async operation, and integrates with direct-I/O accounting.

## Subrequest Handling

- `netfs_prepare_dio_read_iterator()` limits each read subrequest by `sreq_max_len` and optional segment limits, traces preparation, copies the current request iterator to `subreq->io_iter`, truncates it, and advances the request iterator.
- `netfs_dispatch_unbuffered_reads()` loops over the request range:
  - allocates subrequests;
  - marks them as server downloads;
  - queues them on the read stream;
  - calls optional filesystem `prepare_read()`;
  - prepares/truncates iterators;
  - updates submitted byte counts;
  - marks `NETFS_RREQ_ALL_QUEUED` at the end;
  - submits via filesystem `issue_read()`;
  - handles pause and failure state.

## Request Execution

- `netfs_unbuffered_read()` validates nonzero request length, calls `inode_dio_begin()`, dispatches subrequests, and either waits synchronously or returns `-EIOCBQUEUED` for async operation.
- The read collector, not this function, is responsible for `inode_dio_end()` after completion.

## Public Entry Points

- `netfs_unbuffered_read_iter_locked()`
  - Expects caller to hold appropriate locks.
  - Returns 0 for zero-length reads without updating atime.
  - Calls `kiocb_write_and_wait()` to flush conflicting writes.
  - Updates atime with `file_accessed()`.
  - Allocates a read request as `NETFS_DIO_READ` or `NETFS_UNBUFFERED_READ`.
  - Extracts user-backed iterators into request-owned bvec storage for async safety, or copies and advances non-user iterators.
  - Sets offloaded collection for async I/O.
  - For sync I/O, advances `ki_pos` by transferred bytes and returns the transferred count.
- `netfs_unbuffered_read_iter()`
  - Brackets the locked helper with `netfs_start_io_direct()` / `netfs_end_io_direct()`.

## Dependencies

Uses netfs request/subrequest objects, read stream collection, iterator extraction/pinning helpers, direct-I/O inode counters, generic write-and-wait helpers, and filesystem `prepare_read` / `issue_read` operations.

## Research Notes

Direct reads intentionally avoid both pagecache and FS-Cache. The code preserves async correctness by taking ownership of user-backed iterators before returning to the caller, since the original iterator cannot be trusted after an async `read_iter()` returns.
