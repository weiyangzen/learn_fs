# File Research: sources/os/linux/linux/fs/xfs/xfs_inode.h

Defines the kernel XFS inode structure, inode state flags, lock flags/subclasses, inline helpers, and exported inode operation prototypes.

Key elements:
- `struct xfs_inode` embeds mount/quota pointers, inode number and imap, data/attr/COW forks, log item pointer, inode locks, pin count, inodegc list node, health bitsets, state flags, size/block/project/extent metadata, unlinked-list pointers, embedded VFS inode, and pending I/O completion work.
- Inline helpers convert between VFS and XFS inodes, select forks, compute fork sizes, test unlinked/attr-fork/COW/reflink/metadir/internal/zoned/bigtime/large-extent-count state, and compute visible file size.
- Defines in-core state flags for reclaim, stale, new, DM field preservation, truncation, EOF/COW block tags, inactive processing, recovery, quotacheck, remapping, and combined reclaim masks.
- Defines IOLOCK, ILOCK, MMAPLOCK shared/exclusive flags plus lockdep subclass encoding for parent, realtime metadata, and inode-number ordered locking.
- Declares namespace operations, locking operations, inode creation/free/truncate/flush helpers, inode release/log-force helpers, unlinked-list recovery, block counting, layout breaking, allocation unit, and dquot allocation interfaces.
- Includes helpers for stable writes and finishing newly instantiated VFS inode setup.

Dependencies:
- Pulls in inode buffer/fork/util definitions and depends on XFS mount, transaction, dquot, bmap, VFS inode, lockdep, DAX, quota, and metadir concepts.

Research notes:
- The lock flag layout reserves low bits for actual locks and high bits for lockdep subclass annotations.
- `XFS_INACTIVATING` and `XFS_NEED_INACTIVE` encode the handoff from VFS reclaim to background metadata cleanup before reclaimable state.
- Internal inode detection differs depending on whether metadata directories are enabled.
