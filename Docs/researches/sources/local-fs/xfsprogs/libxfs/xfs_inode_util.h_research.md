# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_util.h

## Role

This header declares inode utility interfaces for flag conversion, inode creation initialization, timestamp updates, unlinked-list management, link count updates, and inode uninitialization.

## Main Contents

- `xfs_flags2diflags`, `xfs_flags2diflags2`, `xfs_dic2xflags`, and `xfs_ip2xflags` expose flag conversion.
- `struct xfs_icreate_args` describes file creation context: idmap, parent inode, device id, mode, and creation flags.
- Creation flags cover tmpfile creation, immediate xattr initialization, and unlinkable metadata/detached files.
- `XFS_ICHGTIME_*` flags identify which inode timestamps to update.
- `xfs_inode_init` initializes a newly allocated inode.
- `xfs_inode_uninit` prepares an inode for freeing/reuse.
- `xfs_iunlink` and `xfs_iunlink_remove` maintain the AGI unlinked list.
- `xfs_droplink` and `xfs_bumplink` update link counts.

## Dependencies

The creation argument comments clarify that callers must provide idmap context for correct ownership inheritance and can use null parent/idmap for roots or detached metadata inodes.

## Research Notes

This header is the public contract for inode lifecycle helpers used by allocation, directory, unlink, and metadata file code. Parent pointer and unlinkable flags directly affect attr fork creation.
