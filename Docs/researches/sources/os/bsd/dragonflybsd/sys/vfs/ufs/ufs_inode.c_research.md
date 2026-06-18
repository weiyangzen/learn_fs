# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_inode.c

## Purpose

Implements UFS vnode inactive and reclaim operations. These handle final-reference cleanup, unlink completion, inode update flushing, quota release, dirhash release, and freeing incore inode memory.

## Main Functions

- `ufs_inactive(struct vop_inactive_args *ap)`: called when the last active reference is dropped. If the inode has no links and the mount is writable, it truncates the file, clears mode/rdev, marks metadata changed, and frees the inode with `ffs_vfree()`. It writes pending inode updates and recycles dead vnodes.
- `ufs_reclaim(struct vop_reclaim_args *ap)`: tears down the vnode-to-inode association. It flushes lazy modifications, removes the inode from the inode hash, releases the device vnode, releases quotas, frees any dirhash, and frees the inode allocation.

## Important Behavior

Unlinked files are not fully freed until inactive processing. The code ensures truncation happens before marking the inode free. Under `INVARIANTS`, reclaim warns and forces an update if a modified inode is being released.

Quota release is conditional on `QUOTA`; directory hash cleanup is conditional on `UFS_DIRHASH`.

## Dependencies And Integration Points

Depends on FFS helpers such as `ffs_truncate()`, `ffs_vfree()`, and `ffs_update()`. Calls `ufs_ihashrem()` and `ufsdirhash_free()`. Uses mount-specific inode allocator type from `ufsmount`.

## Notes For Future Work

- `vp->v_data` is cleared before inode memory is freed.
- The reclaim path explicitly tolerates stale file-handle inodes where `ip` is null or mode is zero.
- Lazy modified special-device inodes are pushed before release.
