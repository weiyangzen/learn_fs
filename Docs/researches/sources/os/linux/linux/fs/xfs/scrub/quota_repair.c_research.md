# File Research: sources/os/linux/linux/fs/xfs/scrub/quota_repair.c

## Role
Repairs quota inode mappings, dquot verifier failures, and dquot fields that quota scrub can identify as nonsensical.

## Dquot Mapping Repair
- `xrep_quota_item_bmap` computes the correct quota-file offset, fills holes/delalloc with real initialized quota blocks, rejects unwritten extents, and updates cached disk addresses.
- `xrep_quota_item_fill_bmap_hole` allocates quota-file blocks, initializes a dquot chunk, and rolls the transaction.

## Dquot Field Repair
- `xrep_quota_item` clamps soft limits to hard limits.
- Counts beyond physical filesystem limits are capped where valid and mark `need_quotacheck`.
- Timers are normalized through quota timer adjustment before logging dirty dquots.

## Disk Block Repair
- `xrep_quota_block` rereads verifier-failing quota blocks without ops, rewrites magic/version/type/id, fixes timers, updates UUID/checksum/LSN, sets buffer type, and logs the block.

## Quota File Repair
- `xrep_quota_data_fork` repairs metadata inode forks, converts unwritten extents, truncates mappings beyond max dquot id, cancels CoW reservations, and fixes quota blocks.
- `xrep_quota_problems` iterates dquots and forces a future quotacheck if counters were suspect.

## Top-Level Flow
- `xrep_quota` repairs the quota inode under ILOCK_EXCL, finishes deferred work, unlocks the inode, fixes dquots, and commits.
