# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_inode.c

## Purpose

Implements transaction helpers for joining inodes to transactions, changing inode timestamps, logging inode dirty regions, and rolling transactions while keeping an inode joined.

## Main Functions

- `xfs_trans_ijoin`
  - Adds a locked inode to a transaction.
  - Initializes inode log item if needed.
  - Records lock flags for commit-time unlock.
- `xfs_trans_ichgtime`
  - Updates ctime and optionally mtime, atime, and creation time.
- `xfs_trans_log_inode`
  - Marks inode fields dirty for transaction commit.
  - Sets transaction dirty state.
  - Handles inode version counter logging.
- `xfs_trans_roll_inode`
  - Logs inode core, rolls the transaction, and rejoins the inode.

## Important Invariants

- Inodes must be exclusively locked before joining or logging.
- Stale inodes must not be joined or logged.
- `XFS_ICHGTIME_CHG` must be set for timestamp updates.
- Inode dirty flags are accumulated in the inode log item and processed later by log item precommit code.
- The inode version counter can avoid core logging if no observer requires it.

## Research Notes

This file is small but transaction-critical. It provides the standard inode logging path used by many metadata operations.
