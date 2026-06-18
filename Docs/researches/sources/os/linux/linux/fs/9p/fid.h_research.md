# File Research: sources/os/linux/linux/fs/9p/fid.h

Defines the internal 9p FID management API and cache-mode helper.

Key behavior:
- Declares FID lookup/add helpers for dentries and inodes.
- `v9fs_parent_fid()` retrieves a parent dentry FID.
- `clone_fid()` clones a FID with a zero-component `p9_client_walk()`.
- `v9fs_fid_clone()` looks up a dentry FID, clones it, and drops the original reference.
- `v9fs_fid_add_modes()` annotates a FID’s mode with client-side cache restrictions:
  - Sets `P9L_DIRECT` if caching is disabled, QID version is zero without `ignoreqv`, direct I/O is requested, or `O_DIRECT` is used.
  - Sets `P9L_NOWRITECACHE` if writeback caching is unavailable, `O_DSYNC` is used, or the mount is synchronous.

Important interactions:
- The mode bits set here drive `vfs_file.c` read/write path selection between cached and unbuffered netfs I/O.
- QID version handling is part of the cache coherency policy.
