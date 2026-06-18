# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot_item_recover.c

Implements log recovery for dquot and quotaoff log items.

Key behavior:
- Dquot readahead skips recovery when quotas are off, the logged dquot payload is missing/too small, or a recovered QUOTAOFF disabled that quota type.
- Dquot pass 2 validates the logged disk dquot, reads the target quota buffer with dquot verifiers, compares on-disk dquot LSN against current recovery LSN for CRC filesystems, and copies/rechecks the recovered dquot.
- Recovered buffers are marked `_XBF_LOGRECOVERY` and queued for delayed writeback.
- QUOTAOFF pass 1 records disabled user/project/group quota types in `log->l_quotaoffs_flag`; dquot item and dquot-buffer recovery consult this state.

This file prevents replay of quota metadata after quotaoff and preserves newer on-disk quota records during recovery.
