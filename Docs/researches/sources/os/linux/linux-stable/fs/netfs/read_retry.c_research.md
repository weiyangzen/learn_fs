# File Research: sources/os/linux/linux-stable/fs/netfs/read_retry.c

Retries failed or short read subrequests.

Key behavior:
- Reissues simple retryable subrequests directly when no renegotiation is needed.
- Converts failed cache reads to server downloads.
- When prepare/read sizing is involved, rebuilds contiguous pending spans and repartitions them according to renegotiated size/segment limits.
- Allocates additional subrequests if a retried span needs more pieces; discards superfluous ones if fewer are needed.
- Marks remaining retryable/failed subrequests failed with `-ENOMEM` when allocation or preparation fails.
- `netfs_retry_reads()` waits for in-progress stream I/O to quiesce before modifying the list.
- `netfs_unlock_abandoned_read_pages()` unlocks any buffered folios left behind by abandoned subrequests.
