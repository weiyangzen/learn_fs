# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iunlink_item.h

This header declares the in-memory log item for unlinked inode pointer updates.

Contents:
- Forward declarations for `xfs_trans`, `xfs_inode`, and `xfs_perag`.
- `struct xfs_iunlink_item`, containing:
  - Embedded `xfs_log_item`.
  - Target inode.
  - Held per-AG pointer.
  - New next unlinked agino.
  - Old agino expected on disk.
- Global cache declaration `xfs_iunlink_cache`.
- Public function `xfs_iunlink_log_inode`.

Role:
- Provides the transaction-facing API for scheduling ondisk unlinked-list pointer updates at transaction precommit.
