# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_vfsops.c

Read completely: 288 lines.

Implements generic ULFS VFS helper operations used by LFS mounts.

Functions:
- `ulfs_start()` currently does nothing and returns success.
- `ulfs_root()` returns the root vnode by calling `VFS_VGET()` for `ULFS_ROOTINO`.
- `ulfs_quotactl()` handles quota control when quota support is compiled in: marks the mount busy, takes `mnt_updating`, dispatches to `lfsquota_handle_cmd()`, releases the lock, and unbusies the mount. Without quota support it returns `EOPNOTSUPP`.
- `ulfs_fhtovp()` converts an LFS file handle to a vnode after the underlying filesystem validates it. It maps `ENOENT` to `ESTALE`, rejects mode-zero, generation-mismatched, or dead inodes, and returns the locked vnode on success.
- `ulfs_init()` initializes shared ULFS resources once, including quotas, dirhash, and extattr subsystems when compiled.
- `ulfs_reinit()` rehashes quota state when enabled.
- `ulfs_done()` tears down shared resources once the init reference count reaches zero.

State:
- `ulfs_initcount` reference-counts global ULFS subsystem initialization across mounts/modules.

Integration:
- Pulls in LFS accessors, mount state, quota common code, optional dirhash, and optional extattr.
- The old quota command switch is preserved under `#if 0` as disabled historical code.

Risks and notes:
- `ulfs_initcount` is a plain static integer; callers are expected to serialize module/filesystem init/teardown appropriately.
- Quota control relies on `mnt_updating` plus `vfs_busy()` to stabilize the mount while passing it to kauth and quota handlers.
