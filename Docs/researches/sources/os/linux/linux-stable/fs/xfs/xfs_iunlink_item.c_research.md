# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iunlink_item.c

This file implements the transaction log item used to update an inode’s ondisk `di_next_unlinked` pointer for XFS unlinked inode lists.

Core structures and operations:
- Global `xfs_iunlink_cache` stores `struct xfs_iunlink_item` objects.
- `IUL_ITEM` converts a generic log item to `xfs_iunlink_item`.
- `xfs_iunlink_item_release` drops the per-AG reference and frees the item.
- `xfs_iunlink_item_sort` sorts log items by inode number.
- `xfs_iunlink_log_dinode` maps the inode cluster buffer, validates that the ondisk old pointer matches `old_agino`, updates `di_next_unlinked`, recalculates the dinode CRC, marks the inode buffer in the transaction, and logs exactly the changed field range.
- `xfs_iunlink_item_precommit` performs the buffer update just before commit, removes the log item from the transaction, and releases it.
- `xfs_iunlink_item_ops` wires release, sort, and precommit hooks.

Public entry:
- `xfs_iunlink_log_inode` allocates and initializes an iunlink log item, captures the inode, per-AG reference, new agino, and old agino, adds it to the transaction, marks the transaction dirty, and marks the item dirty.
- It validates `next_agino` and current `i_next_unlinked`, rejects non-null no-op pointer updates as corruption, and treats null-to-null as a no-op.

Design reason:
- The precommit hook ensures inode cluster buffers are logged in correct order relative to other inode cluster buffers while updating unlinked-list pointers.

Risk notes:
- The old pointer check protects against stale or corrupted unlinked list state.
- The code avoids logging stale inode buffers because doing so could incorrectly clear stale state during inode cluster freeing.
