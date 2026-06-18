# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_util.h

This header declares inode utility functions and the inode creation argument structure.

Key contents:
- Flag conversion APIs:
  - `xfs_flags2diflags`
  - `xfs_flags2diflags2`
  - `xfs_dic2xflags`
  - `xfs_ip2xflags`
- Project inheritance helper `xfs_get_initial_prid`.
- `struct xfs_icreate_args`, carrying idmap, parent inode, device number, mode, and creation flags.
- Creation flags:
  - `XFS_ICREATE_TMPFILE`
  - `XFS_ICREATE_INIT_XATTRS`
  - `XFS_ICREATE_UNLINKABLE`
- Timestamp-change flags for `xfs_trans_ichgtime`.
- Prototypes for inode initialization, uninitialization, unlinked-list operations, and link count updates.

Integration:
- Used by inode allocation/create paths, metadir creation, quota inode creation, unlink/inactivation, and transaction code.

Risk notes:
- The comments document idmap responsibilities because XFS only partially relies on VFS inheritance behavior.
- `XFS_ICREATE_UNLINKABLE` is important for parent-pointer behavior; callers creating detached metadata must choose flags carefully.
