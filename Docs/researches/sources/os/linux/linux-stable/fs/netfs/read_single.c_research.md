# File Research: sources/os/linux/linux-stable/fs/netfs/read_single.c

Implements synchronous single-blob reads for monolithic netfs objects such as AFS directories.

Key behavior:
- `netfs_single_mark_inode_dirty()` marks the inode dirty after server download if cached contents should be stored locally.
- Begins a cache read operation when possible; otherwise falls back to server download.
- Allows exactly one subrequest for the object, though that subrequest may later be retried.
- Dispatches either backend cache read or filesystem `issue_read()`.
- `netfs_read_single()` allocates a request, assigns caller iterator as the buffer, dispatches, waits synchronously, and drops the request.

Special case:
- If object is cache-only and caching is unavailable, dirty marking is skipped.
