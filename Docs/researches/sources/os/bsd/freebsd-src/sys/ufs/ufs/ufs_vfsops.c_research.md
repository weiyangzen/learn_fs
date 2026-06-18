# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_vfsops.c

## Purpose
Provides common UFS VFS-level helpers: root lookup, quotactl dispatch, and module-level initialization/uninitialization.

## Key entry points
- `ufs_root()` returns the filesystem root vnode by calling `VFS_VGET()` on `UFS_ROOTINO`.
- `ufs_quotactl()` decodes quota subcommands, resolves default UID/GID for `id == -1`, validates quota type, and dispatches to quota implementation functions.
- `ufs_init()` initializes optional quota and directory-hash subsystems.
- `ufs_uninit()` tears down optional quota and directory-hash subsystems.

## Quotactl behavior
When `QUOTA` is not compiled, `ufs_quotactl()` returns `EOPNOTSUPP`. With quota support, it dispatches:
- `Q_QUOTAON` to `quotaon()`.
- `Q_QUOTAOFF` with mount reference and write-start handling, then `quotaoff()`.
- 32-bit and 64-bit set/get quota and set-use commands.
- `Q_GETQUOTASIZE`.
- `Q_SYNC` to `qsync()`.

For `Q_QUOTAOFF`, the function deliberately drops the mount busy state after taking a reference and starts a write operation before calling into quota shutdown, then restores completion with `vn_finished_write()` and `vfs_rel()`.

## Dependencies
Defines `M_UFSMNT` for UFS mount allocations. Uses optional `QUOTA` and `UFS_DIRHASH` initialization paths and quota command constants from UFS quota headers.

## Research notes
This file is small but important as the public VFS dispatch layer for common UFS behavior. Filesystem-specific mount code supplies the actual `struct mount` and `struct ufsmount`; this file handles generic UFS root and quota plumbing.
