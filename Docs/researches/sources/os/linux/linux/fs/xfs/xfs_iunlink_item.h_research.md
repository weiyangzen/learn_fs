# File Research: sources/os/linux/linux/fs/xfs/xfs_iunlink_item.h

## Role
Declares the in-memory iunlink log item structure and the helper for logging unlinked-list pointer changes.

## Main Declarations
- `struct xfs_iunlink_item` embeds `struct xfs_log_item`, points to the inode and perag, and records new and old next-agino values.
- `xfs_iunlink_cache` exposes the item kmem cache.
- `xfs_iunlink_log_inode` joins an iunlink update to a transaction.

## Interactions
Consumed by unlinked inode list maintenance and implemented by `xfs_iunlink_item.c`. The structure records exactly the state needed to verify and update `di_next_unlinked` during precommit.

## Invariants
The item is not a persistent log replay item; it is an in-memory transaction ordering helper whose state must be consumed before commit.
