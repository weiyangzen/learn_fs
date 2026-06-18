# File Research: sources/os/linux/linux/fs/netfs/read_collect.c

Collects, assesses, unlocks, completes, and retries netfs read subrequests.

Key responsibilities:
- Consumes completed read subrequests in stream order.
- Advances collected and cleaned positions.
- Unlocks folios when all data covering them has arrived or been zero-filled.
- Detects short reads, EOF, retry requests, cache read failures, and permanent server failures.
- Completes direct/unbuffered/single reads and invokes callbacks.
- Handles cache-read completion callbacks.

Important exported APIs:
- `netfs_read_subreq_progress()`.
- `netfs_read_subreq_terminated()`.
- `netfs_cache_read_terminated()`.

Important internal APIs:
- `netfs_read_collection()`.
- `netfs_read_collection_worker()`.
- `netfs_cancel_read()`.

Important behavior:
- Buffered reads can mark downloaded folios for copy-to-cache.
- Short reads may zero unread tails if EOF or clear-tail flags are set.
- Cache read failures become retryable server downloads.
- Server download failures become request failures.
- Completed DIO/unbuffered reads flush destination pages, update `ki_pos`, call `ki_complete`, and end DIO.
- Single-object reads mark inode dirty when data downloaded from server should be cached.

Concurrency model:
- Uses stream list head ordering.
- Reads `IN_PROGRESS` with acquire semantics before counters.
- Wakes waiters by clearing `NETFS_RREQ_IN_PROGRESS`.
