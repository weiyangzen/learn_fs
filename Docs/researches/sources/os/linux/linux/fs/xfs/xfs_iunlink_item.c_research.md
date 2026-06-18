# File Research: sources/os/linux/linux/fs/xfs/xfs_iunlink_item.c

## Role
Implements an in-memory-only log item used to order updates to the on-disk unlinked inode list. The item runs at transaction precommit to update a dinode's `di_next_unlinked` field in the correct buffer logging order.

## Main Structures and Entry Points
- `xfs_iunlink_cache` is the kmem cache for `struct xfs_iunlink_item`.
- `xfs_iunlink_log_inode` allocates and joins an iunlink item to a transaction.
- `xfs_iunlink_item_precommit` updates the dinode before commit and releases the item.
- `xfs_iunlink_log_dinode` reads the inode cluster buffer, verifies the old pointer, writes the new pointer, updates CRC, and logs the precise buffer range.
- `xfs_iunlink_item_ops` provides release, sort, and precommit callbacks.

## Behavior
The public function validates the new and old AG inode pointers, treats a no-op NULL-to-NULL transition as success, rejects a non-NULL self-transition as corruption, saves the inode, perag, new pointer, and old pointer into a dirty log item, and marks the transaction dirty. At precommit, the item maps the inode buffer and updates `di_next_unlinked` unless the buffer is stale because the transaction may be freeing the inode cluster.

## Interactions
Used by unlinked inode list update code to coordinate dinode logging with transaction ordering. Holds a passive perag reference until release. Uses inode buffer mapping, transaction buffer logging, inode verifier errors, tracepoints, and log item sorting by inode number.

## Invariants and Error Handling
- The on-disk old pointer must match the in-core saved old pointer; mismatch is `-EFSCORRUPTED`.
- Stale inode buffers are not relogged because doing so would clear stale state incorrectly.
- Precommit always removes the log item from the transaction and frees it after attempting the dinode update.
