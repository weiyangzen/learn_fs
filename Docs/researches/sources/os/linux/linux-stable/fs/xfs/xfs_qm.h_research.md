# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_qm.h

## Purpose
Defines quota manager in-core state, default quota limit structures, quota transaction accounting layout, and syscall-facing quota manager prototypes.

## Main Types and Constants
`struct xfs_quotainfo` stores per-type dquot radix trees, quota inode pointers, optional quota metadir inode, dquot LRU, quotaoff serialization lock, dquot chunk geometry, default user/group/project limits, shrinker pointer, expiry timestamp range, and live repair hook lists.

`struct xfs_def_quota` groups default block, inode, and realtime-block hard/soft limits plus grace period lengths. `struct xfs_dquot_acct` stores transaction-local dquot deltas for user, group, and project quotas, with `XFS_QM_TRANS_MAXDQS` entries per type.

## Public API
Declares quota syscall helpers for quotaon/off, quota file truncation, getquota/getquota_next, and setqlim. It also declares transaction dquot mutation helpers, quota inode loading, quotainfo destruction, and default quota lookup helpers.

## Invariants
`XFS_IS_DQUOT_UNINITIALIZED` identifies empty dquots with no limits and no usage. `xfs_dquot_tree`, `xfs_quota_inode`, and `xfs_get_defquota` switch strictly by user/group/project dquot type and assert on invalid types.
