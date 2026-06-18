# File Research: sources/os/linux/linux/fs/netfs/objects.c

Handles lifetime, allocation, refcounting, cleanup, and tracing for netfs I/O requests and subrequests.

Important APIs:
- `netfs_alloc_request()`.
- `netfs_get_request()`.
- `netfs_put_request()`.
- `netfs_put_failed_request()`.
- `netfs_alloc_subrequest()`.
- `netfs_get_subrequest()`.
- `netfs_put_subrequest()`.
- `netfs_clear_subrequests()`.

Important behavior:
- Requests and subrequests are mempool-backed to survive memory pressure.
- Requests start with refcount 2 and `NETFS_RREQ_IN_PROGRESS` set.
- Read origins get read collection work; write origins get write collection work.
- Optional netfs `init_request`, `free_request`, and `free_subrequest` hooks are honored.
- Request cleanup cancels collector work, removes proc visibility, clears subrequests, ends cache operation, unpins direct bvec pages, clears rolling buffer, and decrements inode I/O count.
- Final request memory free is RCU-delayed.
- Subrequests hold a reference on the parent request.

Risk/attention points:
- Mempool allocation loops sleep/retry indefinitely.
- `netfs_put_failed_request()` assumes the request is newly allocated with exactly two refs.
