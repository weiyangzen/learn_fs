# File Research: sources/os/linux/linux/fs/xfs/xfs_quota.h

## Role

Kernel-facing XFS quota interface header. Defines transaction quota accounting records, dquot attachment checks, quotacheck-needed checks, and CONFIG-dependent stubs.

## Main Contents

- `XFS_NOT_DQATTACHED`: tests whether an inode lacks any enabled quota dquot.
- `XFS_QM_NEED_QUOTACHECK`: checks superblock checked bits against enabled quota accounting.
- `xfs_quota_chkd_flag`: maps quota type to checked flag.
- `struct xfs_dqtrx`: per-dquot transaction deltas/reservations for data blocks, realtime blocks, delayed allocation, and inode counts.
- `enum xfs_apply_dqtrx_type` and `struct xfs_apply_dqtrx_params`: hook payloads for applying or unreserving transaction quota deltas.
- Public quota operation declarations when `CONFIG_XFS_QUOTA` is enabled.
- No-op stubs when quota support is disabled, allowing call sites to compile cleanly.
- `xfs_quota_unreserve_blkres`: small helper to return reserved quota blocks by applying a negative reservation.

## Live Hooks

When `CONFIG_XFS_LIVE_HOOKS` is enabled, declares hook setup/add/remove/enable/disable functions used by online repair to observe quota transaction deltas.

## Dependencies

Includes quota definitions and forward declarations for transactions and buffers. Used broadly across inode, transaction, bmap, reflink, and mount paths that need quota accounting.
