# File Research: sources/os/linux/linux/fs/xfs/xfs_iwalk.h

## Role
Declares XFS inode walking and inode-btree walking APIs plus callback types and flags.

## Main Declarations
- `xfs_iwalk_fn` callback receives mount, transaction, inode number, and caller data for allocated inode walks.
- `xfs_iwalk` performs single-threaded allocated inode walking.
- `xfs_iwalk_threaded` performs per-AG threaded allocated inode walking.
- `XFS_IWALK_SAME_AG` restricts iteration to the allocation group containing `startino`.
- `xfs_inobt_walk_fn` callback receives mount, transaction, AG number, inobt record, and caller data.
- `xfs_inobt_walk` walks raw inode btree records.

## Interactions
Used by bulkstat/inumbers and any XFS code that must scan allocated inodes or inode allocation records without embedding btree traversal details.

## Invariants
Callbacks return 0 to continue or any nonzero value to stop and propagate. `-ECANCELED` is documented as a safe sentinel because the walkers do not generate it internally.
