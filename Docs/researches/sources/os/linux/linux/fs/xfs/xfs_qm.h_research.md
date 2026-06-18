# File Research: sources/os/linux/linux/fs/xfs/xfs_qm.h

## Role

Internal quota manager header. Defines quota defaults, per-mount quota manager state, transaction quota accounting containers, and syscall-level quota manager entry points.

## Main Contents

- `XFS_DQITER_MAP_SIZE`: limits bmap entries fetched while iterating quota file extents during quotacheck.
- `XFS_IS_DQUOT_UNINITIALIZED`: detects dquots with no limits and no usage.
- `struct xfs_quota_limits`: hard/soft defaults plus grace timer.
- `struct xfs_def_quota`: default block, inode, and realtime block quota limits per quota type.
- `struct xfs_quotainfo`: per-mount quota state containing dquot radix trees, quota inodes, quota metadir inode, dquot LRU, dquot counts, quotaoff mutex, dquot chunk geometry, defaults, shrinker, expiry range, and live quota hooks.
- `xfs_dquot_tree` and `xfs_quota_inode`: select per-type radix tree or quota inode.
- `struct xfs_mod_ino_dqtrx_params`: hook payload for quota transaction modifications.
- `struct xfs_dquot_acct`: per-transaction arrays of dquot changes for user/group/project quota types.
- Default grace periods: one week for block, realtime block, and inode soft-limit timers.

## Exported Interfaces

Declares internal quota transaction functions (`xfs_trans_mod_dquot`, `xfs_trans_dqjoin`, `xfs_trans_log_dquot`), syscall helpers (`xfs_qm_scall_*`), quotainfo destruction, default-quota lookup, and quota inode loading.

## Dependencies

Includes dquot log item and dquot definitions. Consumed mainly by quota manager implementation, quota syscalls, quota ops, and transaction quota accounting code.
