# File Research: sources/os/linux/linux-stable/fs/gfs2/log.h

Declares the public log-management interface used by GFS2 transaction, inode, glock, quota, mount, and recovery code.

Key contents:
- Defines `GFS2_LOG_FLUSH_MIN_BLOCKS` as the minimum space reserved for revoke/header work during flushes.
- Provides `gfs2_ordered_add_inode()`, which adds non-journaled-data inodes to the ordered write list when the filesystem is in ordered mode.
- Declares reservation, release, flush, commit, AIL, revoke, ordered-inode, and logd APIs implemented in `log.c`.

The header is a narrow contract for journal accounting and flush operations. Callers depend on its reservation functions to preserve log space invariants and on `gfs2_log_flush()`/`gfs2_log_commit()` for transaction durability.
