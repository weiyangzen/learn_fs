# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_inode.c

## Purpose

`xfs_trans_inode.c` implements transaction helpers for joining inodes to transactions, changing timestamps, marking inode log items dirty, and rolling transactions while keeping an inode joined.

## Main Content

- `xfs_trans_ijoin`:
  - Requires the inode to be exclusively locked.
  - Initializes the inode log item if needed.
  - Records lock flags for commit-time unlock.
  - Clears per-transaction dirty state.
  - Adds the inode log item to the transaction.
- `xfs_trans_ichgtime`:
  - Updates ctime and optionally mtime, atime, and creation time.
  - Requires the inode to be locked and joined to the supplied transaction.
- `xfs_trans_log_inode`:
  - Marks the transaction dirty.
  - Sets inode log item dirty flags.
  - Bumps i_version once per transaction when configured and needed.
- `xfs_trans_roll_inode`:
  - Logs inode core.
  - Rolls the transaction.
  - Rejoins the inode to the new transaction.

## Key Interfaces and Invariants

- Joined inodes must not already have pending transaction lock flags.
- Stale inodes must not be joined or logged.
- Timestamp updates assert ctime change intent.
- Inode log item precommit later handles actual inode serialization; this file only records dirty state.
- i_version updates are avoided when possible unless core logging is already required.

## Dependencies

Depends on inode log items, transaction internals, VFS inode timestamp/version helpers, and XFS inode locking state.
