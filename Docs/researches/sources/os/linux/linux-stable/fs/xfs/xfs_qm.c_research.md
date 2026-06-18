# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_qm.c

## Purpose
Implements core XFS quota manager lifecycle and quota accounting glue: quota inode discovery/creation, quotainfo setup/teardown, dquot cache purging and reclaim, inode dquot attach/detach, mount-time quotacheck, vnode operation helpers, and enforcement-boundary detection.

## Main APIs
- `xfs_qm_mount_quotas` initializes quota state at mount, creates/loads quota inodes, runs quotacheck when needed, and syncs superblock quota flags.
- `xfs_qm_unmount`, `xfs_qm_unmount_quotas`, and `xfs_qm_destroy_quotainfo` release dquots, quota inodes, shrinkers, radix trees, and locks.
- `xfs_qm_dqattach`, `xfs_qm_dqattach_locked`, and `xfs_qm_dqdetach` manage inode-held user/group/project dquot references.
- `xfs_qm_qino_load` and `xfs_qm_qino_alloc` load or create quota metadata inodes, including metadir quota files and legacy superblock quota inode fields.
- `xfs_qm_vop_dqalloc`, `xfs_qm_vop_chown`, `xfs_qm_vop_rename_dqattach`, and `xfs_qm_vop_create_dqattach` support create, chown, rename, and inode creation quota accounting.
- `xfs_inode_near_dquot_enforcement` detects whether an inode is near quota hard/soft/preallocation limits.

## Key Behavior
The dquot cache is organized as per-type radix trees plus an LRU shrinker. `xfs_qm_dquot_walk` batch-walks radix trees and restarts if busy dquots are skipped. Purge and reclaim paths avoid resurrecting dead dquots, wait for pins/flush locks where needed, detach attached buffers, remove AIL state, delete radix-tree entries, and update quota statistics.

Mount initialization creates `struct xfs_quotainfo`, initializes LRU and tree locks, loads or creates quota inodes, computes dquot chunk geometry, initializes expiry ranges for legacy or bigtime dquots, imports default limits and grace periods from id-0 dquots, registers the shrinker, and sets up live quota hooks.

Mount-time quotacheck resets all on-disk dquot counters, scans every non-quota and non-metadir inode, reloads incomplete unlinked inodes, counts data/realtime blocks, updates in-core dquots and attached dquot buffers, flushes all dirty dquots, writes buffers, and marks quota check flags. On failure it flushes inodegc, purges cached dquots, destroys quotainfo, resets superblock quota flags, and marks quotacheck health sick.

Quota inode handling supports both legacy superblock inode numbers and metadata-directory quota files. V4 group/project quota inode sharing is handled by loading the opposite field when separate project quota inode support is absent. Metadir filesystems prepare the superblock quota feature, create `/quotas` and per-type quota files, and retain the quota directory inode only when online scrub is enabled.

Vnode quota helpers attach dquots before metadata-changing operations, allocate destination dquots for ownership changes, transfer block/inode/realtime counts during chown, attach dquots to new inodes, and account delayed allocation reservations specially when ownership changes.

## Dependencies
Depends on dquot cache/flush helpers, transaction and log item APIs, inode walk and inodegc, quota metadata inode helpers, radix trees, list LRU shrinker, buffer delayed-write lists, superblock logging, health flags, realtime group metadata, and live hook infrastructure.

## Failure Handling
Quotacheck treats dquot verifier failures as repairable during counter reset by rereading without validation and rewriting repaired blocks. Realtime quota mounting is disabled for unsupported non-rtgroup or zoned configurations. Corrupt quota inode fields, missing metadir inodes, failed dquot flushes, and failed inode scans can disable quotas and mark the filesystem quota health state sick.
