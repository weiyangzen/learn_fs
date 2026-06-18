# File Research: sources/local-fs/xfsprogs/libxfs/xfs_trans_inode.c

This file implements transaction helpers for inode log items: joining locked inodes to transactions, updating timestamps transactionally, logging inode dirty fields, and rolling a transaction while keeping an inode joined.

`xfs_trans_ijoin` requires an exclusively locked inode, initializes its inode log item if needed, records lock flags that should be released at transaction commit, asserts the inode is not stale, clears per-transaction dirty flags, and adds the log item to the transaction. The inode must not already be associated with another transaction.

`xfs_trans_ichgtime` updates ctime and optionally mtime, atime, and creation time while the inode is exclusively locked and joined to the transaction. It asserts that ctime is part of any timestamp change.

`xfs_trans_log_inode` marks a joined inode dirty in the transaction. It sets `XFS_TRANS_DIRTY`, asserts the inode log item exists and the inode is exclusively locked/non-stale, conditionally increments the VFS inode version the first time the inode is logged in a transaction, and ORs the requested inode log flags into `ili_dirty_flags`.

`xfs_trans_roll_inode` logs the inode core, rolls the transaction, and rejoins the inode to the new transaction if the roll succeeds. This is used by code paths that must continue modifying an inode across transaction boundaries.
