# File Research: sources/os/linux/linux/fs/netfs/read_single.c

Supports synchronous reads of single monolithic netfs objects, such as AFS directory blobs.

Important exported APIs:
- `netfs_single_mark_inode_dirty()`.
- `netfs_read_single()`.

Key responsibilities:
- Reads one object into a caller-provided iterator using one subrequest at a time.
- Tries cache first when available, otherwise downloads from server.
- Marks object inode dirty after server download if data should be stored in cache.
- Pins cache cookie for writeback when needed.

Important behavior:
- `netfs_read_single()` allocates a `NETFS_READ_SINGLE` request, begins cache read if possible, dispatches one subrequest, waits synchronously, and returns transferred/error.
- The buffer may be larger than content; unused beyond EOF is handled by read completion logic.
- Cache-only dirty marking is skipped if no cache is enabled and `NETFS_ICTX_SINGLE_NO_UPLOAD` is set.
