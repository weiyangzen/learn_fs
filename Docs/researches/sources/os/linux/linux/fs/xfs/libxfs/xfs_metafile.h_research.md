# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_metafile.h

This header declares metadata file helpers and defines required inode flags for metadata files and directories.

Key contents:
- `xfs_metafile_type_str`.
- `XFS_METAFILE_DIFLAGS`, requiring immutable, sync, noatime, nodump, and nodefrag.
- `XFS_METADIR_DIFLAGS`, adding nosymlinks for metadata directories.
- APIs to set/clear metadata inode flags.
- Metadata file reservation APIs:
  - `xfs_metafile_resv_critical`
  - `xfs_metafile_resv_alloc_space`
  - `xfs_metafile_resv_free_space`
  - `xfs_metafile_resv_free`
  - `xfs_metafile_resv_init`
- External kernel/userspace-specific inode lookup hooks:
  - `xfs_trans_metafile_iget`
  - `xfs_metafile_iget`

Integration:
- Used by metadir creation, inode verification, metadata file loading, and allocation paths.

Risk notes:
- Required flag definitions are part of metadata inode validation in `xfs_inode_buf.c`.
- External lookup hooks must enforce expected metadata type and inode validity.
