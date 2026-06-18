# File Research: sources/os/linux/linux-stable/fs/netfs/main.c

Initializes the netfs support library module.

Key behavior:
- Defines module metadata and `netfs_debug` module parameter.
- Creates request and subrequest slab caches plus mempools.
- Creates `/proc/fs/netfs` and active request listing when procfs is enabled.
- Creates `/proc/fs/netfs/stats` when FS-Cache stats are enabled.
- Calls `fscache_init()` after netfs core allocation/proc setup.
- Teardown reverses FS-Cache, proc, mempool, and slab setup.
- Proc request listing reports request id, origin, refs, flags, error, and coverage.

Important exported state:
- `netfs_io_requests`, `netfs_proc_lock`, `netfs_request_pool`, and `netfs_subrequest_pool`.
