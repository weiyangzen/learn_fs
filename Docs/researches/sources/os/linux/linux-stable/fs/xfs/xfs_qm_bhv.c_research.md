# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_qm_bhv.c

## Purpose
Provides quota behavior hooks used outside the core quota manager: quota-aware `statvfs`, mount-time quota state validation, deferred quota mounting, and metadir quota state resumption.

## Main APIs
- `xfs_qm_statvfs` constrains `kstatfs` block and inode availability to the current project quota limits for project-quota directory trees.
- `xfs_qm_newmount` reconciles requested mount quota flags with on-disk quota flags and decides whether quotas can be mounted immediately or must be delayed until log recovery finishes.
- `xfs_qm_resume_quotaon` restores quota accounting/enforcement from the superblock for metadir filesystems when no explicit mount quota options were supplied.

## Key Behavior
Project quota statvfs picks data or realtime block resources according to the inode’s realtime inheritance/realtime state and clamps filesystem totals/free counts to soft limits, falling back to hard limits.

Mount validation prevents quota state changes on read-only or norecovery mounts because changing quota state would require superblock transactions. If quota accounting is already consistent and no quotacheck is needed, quotas are mounted immediately; otherwise quota flags are saved and temporarily cleared until the filesystem is ready.

## Dependencies
Uses dquot lookup/release, project id from inodes, VFS `kstatfs`, superblock quota flags, mount quota flags, readonly/norecovery checks, and metadir feature detection.
