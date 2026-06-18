# File Research: sources/os/linux/linux/fs/netfs/write_retry.c

Implements retry handling for netfs write streams.

Key responsibilities:
- Waits for all active write streams to quiesce.
- Reissues retryable write subrequests.
- Renegotiates write sizes through stream `prepare_write`.
- Splits or discards subrequests when retry sizing changes.
- Allocates additional subrequests when a remaining span requires more pieces.

Important API:
- `netfs_retry_writes()`.

Important behavior:
- Retries are per stream; upload streams may call netfs `retry_request()`.
- If a stream has no `prepare_write`, retry resets the iterator and resubmits directly.
- With `prepare_write`, retry rebuilds contiguous spans, applies `netfs_limit_iter()`, and preserves boundary flags where needed.
- Stream sources drive retry accounting: server upload increments upload stats, cache write increments cache write stats.
- Contains TODO hooks for future encrypted-content read-modify-write handling.
