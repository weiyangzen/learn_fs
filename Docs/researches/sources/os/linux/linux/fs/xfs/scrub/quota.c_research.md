# File Research: sources/os/linux/linux/fs/xfs/scrub/quota.c

## Role
Scrubs one quota type’s quota inode and dquot records.

## Setup
- `xchk_quota_to_dqtype` maps scrub type to user, group, or project quota type.
- `xchk_setup_quota` verifies quotas are enabled, installs the quota inode as the live inode, sets up filesystem scrub state, and takes the quota inode ILOCK.

## Quota File Checks
- `xchk_quota_data_fork` runs metadata inode fork checks, then rejects unwritten/delalloc extents and mappings beyond the maximum dquot id range.
- `xchk_quota_item_bmap` verifies each dquot’s file offset, backing mapping, disk address, and written extent state.

## Dquot Checks
- `xchk_quota_item` checks dquot id ordering, bmap backing, soft/hard limit consistency, physical count sanity, inode count sanity, and timer state.
- Hard limits larger than filesystem size and usage over hard limits are warnings in cases administrators can create.
- On reflink filesystems, block usage can exceed physical blocks without being immediate corruption.

## Top-Level Flow
- `xchk_quota` checks the quota inode first, drops ILOCK_EXCL, iterates dquots with `xchk_dquot_iter`, and stops early on corruption.
