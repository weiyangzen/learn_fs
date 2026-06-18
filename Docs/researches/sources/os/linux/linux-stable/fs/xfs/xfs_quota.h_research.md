# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_quota.h

## Purpose
Declares kernel-only quota integration APIs and transaction quota accounting structures, with no-op stubs when `CONFIG_XFS_QUOTA` is disabled.

## Main Types and Macros
`XFS_NOT_DQATTACHED` detects whether an inode is missing any dquot required by currently enabled quota accounting. `XFS_QM_NEED_QUOTACHECK` determines whether enabled quota types lack checked flags in the superblock.

`struct xfs_dqtrx` tracks per-transaction quota reservations and deltas for data blocks, delayed blocks, realtime blocks, delayed realtime blocks, and inode counts. `struct xfs_apply_dqtrx_params` describes hook metadata for applying transaction quota deltas.

## Public API
When quota support is enabled, the header declares transaction dquot accounting, quota reservation, inode dquot attach/detach, create/chown/rename quota helpers, statvfs quota adjustment, mount/unmount quota hooks, enforcement-boundary checks, block reservation helpers, and optional live hook registration.

## Configuration Behavior
Without `CONFIG_XFS_QUOTA`, quota operations compile to no-ops or success-returning stubs so callers can be written unconditionally. Live hook helpers similarly become no-ops when live hooks are not built.

## Dependencies
Exposes contracts between transaction code, inode operations, mount code, dquot internals, quotactl handling, and optional online repair/live hook code.
