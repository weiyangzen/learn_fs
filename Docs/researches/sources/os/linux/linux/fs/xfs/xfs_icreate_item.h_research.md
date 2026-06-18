# File Research: sources/os/linux/linux/fs/xfs/xfs_icreate_item.h

Declares the in-memory inode-create log item and its logging entry point.

Key elements:
- `struct xfs_icreate_item` embeds a generic `xfs_log_item` and the `xfs_icreate_log` format payload.
- Exposes `xfs_icreate_cache`.
- Declares `xfs_icreate_log` for transaction code that allocates inode chunks.

Dependencies:
- Depends on XFS transaction, inode allocation, AG block, and log-format types.

Research notes:
- The public surface is intentionally minimal because formatting/recovery details live in `xfs_icreate_item.c`.
