# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot.h

Defines XFS in-core dquot structures and public quota helper APIs.

Key contents:
- `struct xfs_dquot_res` tracks reserved count, actual count, hard/soft limits, and grace timer for blocks, inodes, and realtime blocks.
- `struct xfs_dquot_pre` stores speculative preallocation watermarks and low-space thresholds.
- `struct xfs_dquot` includes LRU/cache linkage, mount/type/id, location in quota inode and buffer, three resource counters, embedded log item, prealloc thresholds, mutex, flush completion, pin count, and waitqueue.
- Inline helpers manage flush locking, quota type extraction, quota-on/enforcement checks, inode-to-dquot lookup, over-limit checks, low-space checks, and reference holds.
- Declares dquot lookup, flush, destroy, timer/limit adjustment, buffer attachment, locking, and initialization routines.

This header is the primary type contract for quota accounting, transaction logging, reclaim, and ioctl-facing quota code.
