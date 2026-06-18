# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_file.c

Purpose: Provides FUSE open/release helpers and local file-handle selection for vnode operations.

Key behavior:
- `fusefs_file_open()` sends `FBT_OPEN` or `FBT_OPENDIR` to the daemon and stores the returned file handle in the node’s per-access-mode handle slot.
- `fusefs_file_close()` sends `FBT_RELEASE` or `FBT_RELEASEDIR` when the session is initialized, clears the local handle slot, and logs non-`ENOSYS` close errors.
- `fusefs_fd_get()` returns the requested handle or falls back to the read/write handle when the requested type is invalid.

Filesystem relevance:
- FUSE protocol wants per-open file handles, while OpenBSD VFS does not expose per-descriptor state to vnode ops; this helper implements the local approximation.
