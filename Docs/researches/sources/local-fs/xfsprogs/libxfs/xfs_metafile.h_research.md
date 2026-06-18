# File Research: sources/local-fs/xfsprogs/libxfs/xfs_metafile.h

## Role

This header declares metadata inode type helpers, mandatory metadata inode flags, metadata reservation APIs, and external inode-get hooks for kernel/userspace-specific code.

## Main Contents

- `xfs_metafile_type_str` maps metadata type enum values to strings.
- `XFS_METAFILE_DIFLAGS` defines mandatory flags for metadata files: immutable, sync, noatime, nodump, and nodefrag.
- `XFS_METADIR_DIFLAGS` adds nosymlinks for metadata directories.
- `xfs_metafile_set_iflag` and `xfs_metafile_clear_iflag` manage metadata inode flags.
- Reservation functions test criticality, allocate/free reservation space, initialize reservations, and release unused reservations.
- `xfs_trans_metafile_iget` and `xfs_metafile_iget` are provided externally by kernel/userspace layers.

## Dependencies

The header depends on metadata file type enum definitions, transactions, inodes, mount state, and allocation args.

## Research Notes

Mandatory metadata flags are part of dinode verifier policy. Any change here must stay aligned with `xfs_dinode_verify_metadir`.
