# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item.h

## Purpose
Declares the in-core dquot log item structure and initializer.

## Main Type
`struct xfs_dq_logitem` embeds the common `xfs_log_item`, points back to the owning dquot, records the LSN captured at the last flush, and contains a spinlock protecting the attached buffer pointer in `li_buf` and the `qli_dirty` flag.

## API
Declares `xfs_qm_dquot_logitem_init`.

## Invariants
`qli_dirty` records whether the dquot was dirtied since the last flush began; it determines whether flush completion can drop the attached buffer reference.
