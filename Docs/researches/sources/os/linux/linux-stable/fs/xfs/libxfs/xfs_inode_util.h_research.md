# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_util.h

## Role
`xfs_inode_util.h` declares utility interfaces for inode flags, inode creation, inode timestamp logging, unlinked-list operations, link count updates, and inode uninitialization.

## Main Definitions
- `struct xfs_icreate_args` carries inode creation context: idmap, parent inode, device number, mode, and creation flags.
- Creation flags distinguish tmpfile creation, immediate xattr initialization, and inodes that can never be linked into the directory tree.
- `XFS_ICHGTIME_*` flags select which inode timestamps `xfs_trans_ichgtime` should update.

## Exported API
- Flag conversion: `xfs_flags2diflags`, `xfs_flags2diflags2`, `xfs_dic2xflags`, and `xfs_ip2xflags`.
- Creation/lifecycle: `xfs_inode_init` and `xfs_inode_uninit`.
- Project id inheritance: `xfs_get_initial_prid`.
- Unlinked/link operations: `xfs_iunlink`, `xfs_iunlink_remove`, `xfs_droplink`, and `xfs_bumplink`.
- Timestamp logging: `xfs_trans_ichgtime`.

## Dependencies
The header is consumed by inode allocation, create/link/unlink paths, metadata directory creation, and transaction code.

## Research Notes
This header is the call contract for creating and retiring inodes. Its creation arguments are intentionally explicit about idmapped ownership and detached/tree-root cases.
