# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_vfsops.c

This file contains the generic VFS-level helpers for UFS-family filesystems. It does not mount FFS itself; instead it provides shared operations used by concrete UFS consumers.

Key responsibilities:
- Start a UFS filesystem.
- Return root and arbitrary inode vnodes.
- Dispatch filesystem quota control operations.
- Convert validated file handles to vnodes.
- Initialize, reinitialize, and tear down shared UFS resources.
- Provide the UFS kernel module command entry point.

Important functions:
- `ufs_start`: Placeholder start operation; currently no work.
- `ufs_root`: Loads `UFS_ROOTINO` with requested lock type.
- `ufs_vget`: Uses `vcache_get` and then locks the vnode.
- `ufs_quotactl`: If quota support is compiled in, marks the mount busy, serializes through `mnt_updating`, and calls `quota_handle_cmd`.
- `ufs_fhtovp`: Generic file-handle-to-vnode helper after lower filesystem validation; rejects stale inodes by generation, zero mode, or removed directory size.
- `ufs_init`: One-time shared initialization for direct-entry pool cache, quotas, dirhash, and extended attributes.
- `ufs_reinit`: Rehashes quota state after vnode table sizing changes.
- `ufs_done`: One-time teardown for quotas, direct-entry cache, dirhash, and extattrs.
- `ufs_modcmd`: Kernel module init/fini entry point.

Important interactions:
- `ufs_direct_cache` is used heavily by directory creation/link/rename code.
- Quota support is conditional on `QUOTA` or `QUOTA2`.
- Dirhash and extended attributes are initialized only when compiled in.
- Module dependency includes `wapbl` when WAPBL is compiled.

Notable behavior:
- `ufs_initcount` makes shared initialization idempotent across multiple UFS-family modules.
- `ufs_quotactl` keeps quota operations under mount update serialization because they may alter mount quota state and call authorization logic.
