# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/quota.h

This header declares quota scrub helpers and the dquot iterator state.

Contents:
- `xchk_quota_to_dqtype`: converts scrub type to user/group/project dquot type.
- `struct xchk_dqiter`: state for walking dquots in a quota file, including scrub context, quota inode, cached bmap record, next id, quota type, and data-fork sequence number.
- `xchk_dqiter_init`
- `xchk_dquot_iter`

The iterator abstraction lets quota scrub, quota repair, quotacheck compare, and quotacheck repair share dquot traversal behavior without duplicating quota-file mapping logic.
