# File Research: sources/os/linux/linux/fs/xfs/xfs_qm.c

## Role

Core XFS quota manager implementation. It owns per-mount quota initialization and teardown, dquot cache walking/reclaim, quotacheck rebuilding, quota inode creation/loading, inode dquot attachment, and vnode-operation helpers for create/chown/rename paths.

## Main Responsibilities

- Maintains dquot radix trees and LRU reclaim through `xfs_qm_dquot_walk`, `xfs_qm_dqpurge`, `xfs_qm_shrink_scan`, and `xfs_qm_dqfree_one`.
- Initializes `struct xfs_quotainfo` in `xfs_qm_init_quotainfo`, including quota inodes, radix trees, quota defaults, expiry ranges, shrinker, and live hooks.
- Supports both classic quota inode fields and metadata-directory quota inode layout via `xfs_qm_init_quotainos` and `xfs_qm_init_metadir_qinos`.
- Runs mount-time quotacheck in `xfs_qm_quotacheck`, resetting on-disk dquot counters, walking all inodes, adjusting dquot usage, flushing dirty dquot buffers, and marking quota health.
- Attaches and detaches user/group/project dquots to regular inodes with `xfs_qm_dqattach_locked`, `xfs_qm_dqattach`, and `xfs_qm_dqdetach`.
- Handles create/chown/rename quota transitions through `xfs_qm_vop_dqalloc`, `xfs_qm_vop_create_dqattach`, `xfs_qm_vop_chown`, and `xfs_qm_vop_rename_dqattach`.

## Important Flows

- Mount:
  `xfs_qm_mount_quotas` rejects unsupported realtime quota combinations, initializes quotainfo, runs quotacheck if needed, clears stale checked flags for disabled quota types, and writes superblock quota flags.
- Quotacheck:
  quota file counters are zeroed with `xfs_qm_reset_dqcounts_buf`; all non-quota, non-metadir inodes are visited by `xfs_iwalk_threaded`; dquot counters are rebuilt by `xfs_qm_quotacheck_dqadjust`; dirty dquots are flushed by `xfs_qm_flush_one`.
- Dquot reclaim:
  reclaim skips referenced, dead, dirty, pinned, or flush-locked dquots; removable dquots are marked dead, isolated from LRU, removed from radix trees, and destroyed.
- Quota inode creation:
  `xfs_qm_qino_alloc` handles legacy group/project quota inode sharing, optional superblock quota-version enablement, metadata inode tagging, and superblock qino updates.

## Locking and Consistency

- `qi_tree_lock` protects dquot radix tree iteration and deletion.
- `qi_quotaofflock` serializes quota-off/enforcement changes.
- Dquot purge coordinates `q_lockref`, `q_qlock`, pin waits, flush locks, AIL state, buffer attachment, and LRU deletion.
- Quotacheck is mount-time only and relies on single-threaded mount context for some otherwise racy-looking operations.
- Metadata directory inodes are excluded from user-visible quota accounting.

## Dependencies

Uses XFS inode walking, bmap, transaction, dquot, buffer, log, health, realtime group, and metadata inode APIs. Public declarations are split across `xfs_qm.h` and `xfs_quota.h`.
