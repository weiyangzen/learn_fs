# File Research: sources/os/linux/linux/fs/9p/v9fs.h

Defines the core 9p session, inode, protocol, and cache-mode data structures.

Key behavior:
- Defines session flags for:
  - Protocol variants: `V9FS_PROTO_2000U`, `V9FS_PROTO_2000L`.
  - Access modes: `single`, `user`, `client`, `any`.
  - POSIX ACLs, xattr disabling, QID-version ignoring, direct I/O, and sync mode.
- Defines cache shortcuts and underlying cache bits:
  - `CACHE_FILE`, `CACHE_META`, `CACHE_WRITEBACK`, `CACHE_LOOSE`, `CACHE_FSCACHE`.
- `struct v9fs_session_info` holds mount/session state, user defaults, selected cache policy, 9p client, rename semaphore, lock timeout, and optional FS-Cache data.
- `struct v9fs_inode` wraps `struct netfs_inode`, a 9p `qid`, cache-validity flags, and a mutex.
- Provides helpers for converting between VFS inode/dentry and session state.
- Provides protocol helpers `v9fs_proto_dotu()` and `v9fs_proto_dotl()`.
- Provides `v9fs_get_inode_from_fid()` and `v9fs_get_new_inode_from_fid()` dispatchers that choose legacy/u vs dotl inode creation.

Important interactions:
- This header is the shared contract across all 9p source files.
- The inode embeds netfs state, which lets `vfs_addr.c` and `vfs_file.c` use netfs helpers for cache and I/O behavior.
