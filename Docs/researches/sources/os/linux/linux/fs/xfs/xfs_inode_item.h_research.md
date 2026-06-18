# File Research: sources/os/linux/linux/fs/xfs/xfs_inode_item.h

Declares the XFS inode log item state and exported inode logging/flush helpers.

Key elements:
- `struct xfs_inode_log_item` embeds the generic log item, backpointer to the inode, transaction lock flags, per-transaction dirty flags, a flush-state spinlock, current/last logged field masks, flush LSN, and commit/datasync sequence numbers.
- `xfs_inode_clean` tests whether an inode has no active log item dirty fields.
- Declares inode item initialization/destruction, flush abort helpers, shutdown abort helper, and old-format conversion.
- Exposes `xfs_ili_cache`.

Dependencies:
- Depends on XFS log item, inode, mount, buffer, bmap record, and log-format definitions.

Research notes:
- `ili_lock` is the key synchronization point between dirtying, flushing, completion, and fsync sequence tracking because those paths hold different inode locks.
