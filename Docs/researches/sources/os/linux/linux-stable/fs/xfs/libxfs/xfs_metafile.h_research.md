# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metafile.h

## Role
`xfs_metafile.h` declares metadata file flag policy, metadata inode flag setters, metadata reservation APIs, and external metadata inode lookup hooks.

## Main Definitions
- `XFS_METAFILE_DIFLAGS` lists mandatory flags for metadata files: immutable, sync, noatime, nodump, and nodefrag.
- `XFS_METADIR_DIFLAGS` extends metadata file flags with nosymlinks for metadata directories.

## Exported API
- Metadata type names: `xfs_metafile_type_str`.
- Flag manipulation: `xfs_metafile_set_iflag` and `xfs_metafile_clear_iflag`.
- Reservation management: `xfs_metafile_resv_critical`, `xfs_metafile_resv_alloc_space`, `xfs_metafile_resv_free_space`, `xfs_metafile_resv_free`, and `xfs_metafile_resv_init`.
- Environment-provided inode lookup: `xfs_trans_metafile_iget` and `xfs_metafile_iget`.

## Dependencies
The header is shared by kernel and userspace libxfs builds; lookup functions are intentionally supplied externally for environment-specific inode handling.

## Research Notes
This header codifies the rule that metadata files are real inodes but must be hidden and protected by mandatory inode flags and separate reservation accounting.
