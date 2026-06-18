# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_qm_syscalls.c

## Purpose
Implements the quota manager syscall backend for enabling/disabling enforcement, truncating quota files, setting quota limits/timers, and retrieving quota usage.

## Main APIs
- `xfs_qm_scall_quotaon` enables quota enforcement bits after verifying accounting is enabled.
- `xfs_qm_scall_quotaoff` disables enforcement bits; accounting shutdown is no longer supported and is ignored with an informational message.
- `xfs_qm_scall_trunc_qfiles` truncates selected quota metadata files when quotas are off.
- `xfs_qm_scall_setqlim` updates quota hard/soft limits, grace timers, id-0 default limits, preallocation limits, and dirty/log state.
- `xfs_qm_scall_getquota` returns quota usage/limits for one id, including default limits for missing non-root dquots.
- `xfs_qm_scall_getquota_next` returns the next initialized dquot at or after a requested id.

## Key Behavior
Quota enforcement changes update superblock quota flags and synchronize the superblock. Runtime in-core enforcement is changed only when accounting is already active in core. Truncation loads the quota inode, truncates extents in a transaction, updates size and timestamps, and releases the inode.

Set-limit operations validate field masks, allocate/load the dquot, join it to a transaction, apply block/realtime/inode limits independently, update id-0 defaults when modifying the root dquot, convert byte limits to filesystem blocks, and use timeout helpers to distinguish default grace periods from per-id expiry timestamps.

Getquota pushes inodegc at the start of scans so pending inode cleanup is reflected. Missing dquots with configured default limits are reported as zero-usage dquots for non-root ids. Timers are hidden from userspace when enforcement is disabled even though XFS keeps them internally.

## Dependencies
Uses quota dquot lookup, transaction reservations, quota inode loading/truncation, superblock sync, VFS `qc_dqblk` masks, inodegc push, limit/timer conversion helpers, and dquot preallocation watermark recalculation.

## Failure Handling
Invalid masks, zero enable flags, enforcement without accounting, read-only superblocks through callers, inconsistent quota state, allocation failures, and missing dquots return standard negative errno values. `-EEXIST` is intentionally used for already-off/already-on cases expected by quota utilities.
