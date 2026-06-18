# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item_recover.c

## Purpose
Implements log recovery for dquot items and quotaoff items.

## Main APIs
- `xlog_dquot_item_ops` provides pass2 readahead and commit replay for `XFS_LI_DQUOT`.
- `xlog_quotaoff_item_ops` records quotaoff state during pass1 for `XFS_LI_QUOTAOFF`.

## Dquot Recovery
Recovery ignores dquot items if mount quota flags are absent or if a matching quotaoff was logged. It validates the logged disk dquot, reads the destination dquot buffer with verifier ops, skips replay when the on-disk dquot LSN is newer on CRC filesystems, copies the logged dquot into place, recalculates CRC, validates the full dquot block, and queues delayed write with `_XBF_LOGRECOVERY`.

## Readahead
Pass2 readahead reads the target dquot buffer unless quota is off, the log vector is missing/too small, or quotaoff already disables that type.

## Quotaoff Recovery
Pass1 inspects quotaoff flags and records user/project/group quota types in `log->l_quotaoffs_flag`, suppressing subsequent dquot item and dquot-buffer replay for those types.
