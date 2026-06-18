# File Research: sources/os/linux/linux/fs/9p/vfs_super.c

Implements 9p superblock, fs_context, mount, statfs, and unmount behavior.

Key behavior:
- `v9fs_fill_super()` initializes superblock size limits, block size based on `maxdata`, magic, super operations, xattr handlers for dotl, time limits, backing device info, readahead/io page settings, and POSIX ACL flag.
- `v9fs_get_tree()`:
  - Allocates a session.
  - Initializes 9p session and root FID.
  - Allocates an anonymous superblock.
  - Selects cached or uncached dentry operations based on cache mode.
  - Creates root inode from the root FID.
  - Fetches ACLs and attaches the root FID to the root dentry.
- `v9fs_kill_super()` kills the anonymous superblock, cancels/closes the 9p session, frees session state, and clears `s_fs_info`.
- `v9fs_umount_begin()` begins client disconnect on forced/unmount paths.
- Dotl `v9fs_statfs()` uses server `statfs` when supported, otherwise falls back to `simple_statfs()`.
- `v9fs_drop_inode()` keeps cached-mode inode retention generic, but always drops inodes for uncached mode to force server attribute freshness.
- Write-inode hooks call `netfs_unpin_writeback()`.
- Defines `fs_context_operations` for parse/get_tree/free.
- `v9fs_init_fs_context()` sets default session/client/fd/RDMA options, including protocol default 9P2000.L and default `msize`.
- Registers the `file_system_type` named `9p`.

Important interactions:
- The cache mode selected in `v9fs.c` controls dentry caching, inode dropping, readahead, and xattr/ACL behavior here.
