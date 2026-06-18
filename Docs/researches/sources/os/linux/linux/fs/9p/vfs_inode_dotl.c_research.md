# File Research: sources/os/linux/linux/fs/9p/vfs_inode_dotl.c

Implements inode operations specific to the 9P2000.L protocol.

Key behavior:
- Uses dotl stat data including generation number for inode matching.
- `v9fs_inode_from_fid_dotl()` fetches `P9_STATS_BASIC | P9_STATS_GEN` and instantiates/reuses inodes.
- Converts Linux open flags to dotl flags with `v9fs_open_to_dotl_flags()`.
- Creation paths use POSIX-like dotl RPCs:
  - `p9_client_create_dotl()`
  - `p9_client_mkdir_dotl()`
  - `p9_client_mknod_dotl()`
  - `p9_client_symlink()`
  - `p9_client_link()`
- New object gid honors parent `S_ISGID` through `v9fs_get_fsgid_for_create()`.
- Creation and mkdir/mknod adjust mode through ACL helpers and set inherited create ACLs after inode instantiation.
- Dotl atomic open mirrors legacy atomic behavior while using dotl open flags and ACL-aware mode creation.
- Dotl getattr fetches `P9_STATS_ALL`, refreshes inode, fills `kstat`, and uses server block size.
- Dotl setattr maps Linux `ATTR_*` bits to 9p dotl attribute flags, flushes dirty data, sends `p9_client_setattr()`, resizes cache/page state on truncate, invalidates attributes, and updates ACLs on chmod.
- `v9fs_stat2inode_dotl()` handles both full basic stat and partial result masks for atime, mtime, ctime, uid, gid, nlink, mode, size, blocks, and generation.
- Dotl symlink following uses `p9_client_readlink()`.
- Dotl hardlink instantiates the new dentry with the existing inode and refreshes link metadata in cached modes.
- Exposes inode operations with xattr and ACL hooks for directories/files; symlinks expose listxattr but no ACL hooks.

Important interactions:
- Reuses common lookup, unlink, rmdir, rename, cache, dentry, and netfs machinery from other 9p files.
- Dotl is the only path where POSIX ACL enforcement is enabled by mount/session logic.
