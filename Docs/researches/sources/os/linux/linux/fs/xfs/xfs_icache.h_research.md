# File Research: sources/os/linux/linux/fs/xfs/xfs_icache.h

Declares public interfaces and control flags for the XFS inode cache, reclaim, blockgc, and inodegc subsystems.

Key elements:
- `struct xfs_icwalk` carries inode-walk filters: flags, uid, gid, project id, minimum file size, and scan limit.
- Defines public inode walk flags for sync mode, uid/gid/project filtering, and minimum file size filtering.
- Defines `xfs_iget` flags for create, untrusted lookup, don’t-cache, incore-only, and no-retry behavior.
- Declares inode allocation/free, reclaim workers/counts/scans, reclaimable marking, blockgc quota/free-space helpers, EOF/COW block tag management, blockgc worker control, inodegc worker control, flush/push/stop/start, and inodegc shrinker registration.

Dependencies:
- Exposes XFS mount, per-AG, inode, dquot, and transaction-facing cache operations to the rest of the filesystem.

Research notes:
- The header name guard still says `XFS_SYNC_H`, reflecting older sync/reclaim grouping, but contents are inode-cache focused.
