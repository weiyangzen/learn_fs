# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iops.h

This header declares XFS inode-operation helpers used outside `xfs_iops.c`.

Exports:
- `xfs_vn_listxattr`
- `xfs_vn_setattr_size`
- `xfs_inode_init_security`
- `xfs_setup_inode`
- `xfs_setup_iops`
- `xfs_diflags_to_iflags`
- Atomic write capability helpers:
  - `xfs_get_atomic_write_min`
  - `xfs_get_atomic_write_max`
  - `xfs_get_atomic_write_max_opt`

Role:
- Connects inode setup, VFS attribute handling, xattr listing, security initialization, and atomic write reporting to the rest of the XFS implementation.
