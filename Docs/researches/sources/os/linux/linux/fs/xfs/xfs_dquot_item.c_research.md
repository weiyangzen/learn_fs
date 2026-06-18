# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot_item.c

Implements transaction log item operations for dquots.

Key behavior:
- Formats a dquot log item as two vectors: `xfs_dq_logformat` plus an on-disk `xfs_disk_dquot` copy.
- Pins/unpins dquots with `q_pincount`, waking waiters when the count drops to zero.
- `xfs_qm_dqunpin_wait` forces the log and waits until a locked dquot is unpinned.
- AIL push tries to lock the dquot, acquire the flush completion, use an attached buffer, flush the dquot, and queue the buffer for delayed writeback.
- Precommit optionally verifies the on-disk-form dquot under expensive debug checks, then attaches a dquot buffer to avoid later reclaim-time allocation.
- Release unlocks the dquot because dquot locking is hidden inside transaction commit.

This file bridges in-memory quota modifications to the generic XFS log item and AIL infrastructure.
