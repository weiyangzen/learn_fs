# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iwalk.h

This header declares XFS inode and inode-btree walk APIs.

Exports:
- `xfs_iwalk_fn`, callback for allocated inode numbers.
- `xfs_iwalk`, single-threaded allocated-inode walk.
- `xfs_iwalk_threaded`, per-AG threaded allocated-inode walk.
- `XFS_IWALK_SAME_AG` and `XFS_IWALK_FLAGS_ALL`.
- `xfs_inobt_walk_fn`, callback for raw inode btree records.
- `xfs_inobt_walk`, single-threaded inode btree record walk.

Semantics:
- Walk callbacks return `0` to continue or nonzero to stop.
- `-ECANCELED` is a special stop value used by callers that need to end iteration without treating it as a native walker error.
- `XFS_IWALK_SAME_AG` constrains iteration to the allocation group containing the starting inode.

Role:
- Provides the common iterator interface used by bulkstat/inumbers and other inode-scanning code.
