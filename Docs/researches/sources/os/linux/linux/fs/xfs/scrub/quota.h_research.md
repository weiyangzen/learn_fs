# File Research: sources/os/linux/linux/fs/xfs/scrub/quota.h

## Role
Declares quota scrub helpers and the dquot iterator state.

## API
- `xchk_quota_to_dqtype` maps scrub type to dquot type.
- `xchk_dqiter_init` initializes quota-file iteration.
- `xchk_dquot_iter` returns referenced dquots one at a time.

## Iterator State
`struct xchk_dqiter` tracks scrub context, quota inode, cached bmap, next id, quota type, and data-fork sequence number used to detect stale mappings.
