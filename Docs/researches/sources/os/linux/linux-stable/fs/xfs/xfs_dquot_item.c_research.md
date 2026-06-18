# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item.c

## Purpose
Implements dquot log item operations for transaction logging, pinning, AIL push, release, and precommit buffer attachment.

## Main Behavior
Dquot log items format as two vectors: an `xfs_dq_logformat` plus the serialized `xfs_disk_dquot`. Pin/unpin updates the dquot pin count and wakes waiters when it reaches zero. `xfs_qm_dqunpin_wait` forces the log before waiting for pins to drain.

## AIL Push
`xfs_qm_dquot_logitem_push` skips pinned or locked dquots, grabs the dquot lock and flush gate, obtains the pre-attached dquot buffer, calls `xfs_qm_dqflush`, and queues the buffer for delayed write. It temporarily drops the AIL lock while doing buffer work.

## Transaction Integration
Release unlocks the dquot because dquot locking is hidden inside transaction commit. Precommit optionally verifies the dquot under `DEBUG_EXPENSIVE` and always attaches the backing buffer so later AIL pushes do not need to allocate/read from reclaim context.

## Public API
`xfs_qm_dquot_logitem_init` initializes the embedded log item, spinlock, back pointer, and dirty-since-flush state.
