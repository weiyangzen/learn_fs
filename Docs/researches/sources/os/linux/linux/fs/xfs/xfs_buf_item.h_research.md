# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_item.h

Declares the in-core XFS buffer log item API and state flags.

Key contents:
- `XFS_BLI_*` flags describe transaction-local and persistent BLI state: held, dirty, stale, logged, inode allocation buffer, stale inode, inode buffer, and ordered.
- `struct xfs_buf_log_item` embeds the common `xfs_log_item`, points at the real `xfs_buf`, stores flags, recursion/refcount state, and one or more `xfs_buf_log_format` records.
- Declares buffer log item lifecycle and logging functions: `xfs_buf_item_init`, `xfs_buf_item_done`, `xfs_buf_item_put`, `xfs_buf_item_log`, and `xfs_buf_item_dirty_format`.
- Declares I/O completion helpers for inode and dquot buffers.
- Exposes `xfs_buf_log_check_iovec` and `xfs_buf_inval_log_space` for recovery/log reservation validation.

This header is the contract between transaction code, buffer code, quota code, inode code, and log recovery.
