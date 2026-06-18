# File Research: sources/os/linux/linux/fs/xfs/xfs_iops.h

## Role
Declares the XFS inode-operation functions and inode setup helpers used outside `xfs_iops.c`.

## Main Declarations
- `xfs_vn_listxattr` from the xattr subsystem.
- `xfs_vn_setattr_size` for explicit size-change handling.
- `xfs_inode_init_security` for LSM security xattr initialization.
- `xfs_setup_inode`, `xfs_setup_iops`, and `xfs_diflags_to_iflags` for VFS inode initialization.
- Atomic write stat helpers: `xfs_get_atomic_write_min`, `xfs_get_atomic_write_max`, and `xfs_get_atomic_write_max_opt`.

## Interactions
Used by inode allocation/read paths and by code that needs to query XFS atomic write capabilities without depending on the full inode operation implementation details.

## Invariants
The header separates setup/stat helper declarations from the private VFS operation tables, which remain internal to `xfs_iops.c`.
