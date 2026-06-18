# File Research: sources/os/linux/linux/fs/netfs/read_retry.c

Implements retry handling for failed or partial netfs read subrequests.

Key responsibilities:
- Waits for outstanding reads to quiesce.
- Reissues retryable subrequests.
- Converts failed cache reads to server downloads.
- Renegotiates read sizes through netfs callbacks.
- Splits or discards subrequests when retry sizing changes.
- Unlocks abandoned read folios at request completion.

Important APIs:
- `netfs_retry_reads()`.
- `netfs_unlock_abandoned_read_pages()`.

Important behavior:
- If no `prepare_read` and no cache resources are involved, retry simply resets iterators and reissues subrequests.
- Otherwise, it rebuilds contiguous retry spans, switches source to `NETFS_DOWNLOAD_FROM_SERVER`, and uses `prepare_read()` plus `netfs_limit_iter()` to enforce max length/segment limits.
- Can allocate additional subrequests if a retry span needs more pieces than before.
- If allocation or preparation fails, remaining retryable subrequests are marked failed.
- `NETFS_RREQ_RETRYING` prevents normal collector wake behavior while streams are quiescing.
