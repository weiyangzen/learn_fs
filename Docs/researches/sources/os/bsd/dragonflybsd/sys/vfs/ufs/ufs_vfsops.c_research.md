# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_vfsops.c

## Purpose

Provides generic UFS VFS-level operations shared by UFS-based filesystems: root vnode lookup, quota command dispatch, one-time initialization, NFS file-handle conversion, and export checks.

## Main Functions

- `ufs_root(struct mount *mp, struct vnode **vpp)`: returns the root vnode by calling `VFS_VGET()` for `UFS_ROOTINO`.
- `ufs_quotactl()`: validates quota command permissions, resolves default uid/gid, busies the mount, and dispatches to quota operations when `QUOTA` is enabled. Returns `EOPNOTSUPP` without quota support.
- `ufs_init(struct vfsconf *vfsp)`: one-time UFS initialization; initializes quota dquot cache when quotas are compiled in.
- `ufs_fhtovp()`: converts a UFS file handle to a vnode and validates generation, mode, and link count to reject stale handles.
- `ufs_check_export()`: looks up export credentials/options for a client address using `vfs_export_lookup()`.

## Important Behavior

Quota permission checks use DragonFly capability checks. Mutating quota commands require `SYSCAP_NOQUOTA_WR`; `Q_GETQUOTA` allows self-query or restricted-root capability; `Q_SYNC` is allowed.

`ufs_fhtovp()` accounts for softdep effective link count if `um_i_effnlink_valid` is set, otherwise uses `i_nlink`.

## Dependencies And Integration Points

Uses `M_UFSMNT` allocation type, `struct ufsmount`, quota functions in `ufs_quota.c`, and export state in `ufsmount.h`.

## Notes For Future Work

- This file is generic UFS glue; actual mount/unmount and FFS-specific operations live elsewhere.
- `rootvp` is accepted by `ufs_fhtovp()` but not used in this implementation.
