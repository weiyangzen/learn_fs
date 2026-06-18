# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot_item.h

Defines the in-core dquot log item.

Key contents:
- `struct xfs_dq_logitem` embeds a common `xfs_log_item`, points back to the owning `xfs_dquot`, records the LSN at the last flush, and uses a spinlock to protect the attached buffer pointer and `qli_dirty`.
- Declares `xfs_qm_dquot_logitem_init`.

The structure supports AIL push and flush completion coordination for quota metadata.
