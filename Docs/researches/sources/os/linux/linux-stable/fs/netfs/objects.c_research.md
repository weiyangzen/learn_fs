# File Research: sources/os/linux/linux-stable/fs/netfs/objects.c

Handles netfs I/O request and subrequest object lifetime.

Key behavior:
- Allocates requests from filesystem-specific pools or global mempools.
- Initializes request origin, mapping, inode, size snapshot, streams, waitqueue, work item, and tracing id.
- Read origins use `netfs_read_collection_worker`; write origins use `netfs_write_collection_worker`.
- Requests start with two refs, including the in-progress/work lifecycle ref.
- Calls filesystem `init_request()` and `free_request()` hooks when present.
- Request free path cancels collection work, removes proc entry, clears subrequests, ends cache operation, unpins direct bvec pages, clears rolling buffer, and decrements inode I/O count.
- Subrequests are also mempool-backed, refcounted, linked to parent request, and traced.
