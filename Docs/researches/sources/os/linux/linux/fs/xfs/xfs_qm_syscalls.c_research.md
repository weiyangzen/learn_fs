# File Research: sources/os/linux/linux/fs/xfs/xfs_qm_syscalls.c

## Role

Implements XFS quota manager operations backing generic quotactl wrappers: enabling/disabling enforcement, truncating quota files, setting limits, and reading quota records.

## Main Responsibilities

- `xfs_qm_scall_quotaoff` disables quota enforcement bits in-core and on-disk, but deliberately does not support disabling quota accounting.
- `xfs_qm_scall_quotaon` enables enforcement after verifying accounting is already enabled.
- `xfs_qm_scall_trunc_qfiles` truncates selected quota files when quotas are fully off.
- `xfs_qm_scall_setqlim` updates block, realtime block, and inode hard/soft limits plus timers for one dquot; ID 0 updates default quota state.
- `xfs_qm_scall_getquota` reads one quota record, returning configured default limits with zero usage for missing nonzero IDs when appropriate.
- `xfs_qm_scall_getquota_next` scans to the next initialized dquot.
- Fill helpers convert internal filesystem-block units to byte-based `qc_dqblk` fields.

## Important Rules

- Limit updates reject hard limits lower than soft limits.
- Timer handling distinguishes default grace period updates for ID 0 from per-dquot grace expiration updates.
- Reporting hides timers when enforcement is disabled, even though internal timers continue to exist.
- Quota scans push inodegc at ID 0 to improve accounting freshness.

## Dependencies

Relies on dquot lookup/allocation, quota transactions, dquot logging, quota defaults from `xfs_quotainfo`, inodegc, superblock syncing, and quota inode loading/truncation.
