# File Research: sources/os/linux/linux/fs/netfs/main.c

Module/init code for generic network filesystem support.

Key responsibilities:
- Defines module metadata and `netfs_debug` module parameter.
- Exports `netfs_sreq` tracepoint.
- Creates request and subrequest slab caches plus mempools.
- Creates `/proc/fs/netfs` and `requests` proc file.
- Creates `stats` proc file when FS-Cache stats are enabled.
- Calls `fscache_init()` after netfs base resources are ready.

Important globals:
- `netfs_request_pool`.
- `netfs_subrequest_pool`.
- `netfs_io_requests`.
- `netfs_proc_lock`.

Important behavior:
- `netfs_requests_seq_show()` displays active request debug id, origin, refcount, flags, error, start/submitted/length.
- Init is registered with `fs_initcall(netfs_init)`.
- Exit tears down FS-Cache, procfs, mempools, and slabs.
