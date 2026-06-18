# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_export.h

## Purpose

Defines XFS-specific NFS export file handle formats and declares handle-to-inode resolution.

## Main Contents

- Documents supported fileid wire formats:
  - no data
  - 32-bit inode plus generation
  - 32-bit inode plus parent
  - 64-bit inode plus generation
  - 64-bit inode plus parent
- Defines packed `struct xfs_fid64`.
- Defines `XFS_FILEID_TYPE_64FLAG`, an on-wire flag indicating 64-bit inode numbers.
- Declares `xfs_nfs_get_inode`.

## Research Notes

The important compatibility note is that NFS fsid inode fields may still be 32-bit outside XFS control; exporting the mountpoint or setting `fsid` is recommended for filesystems with 64-bit inode numbers.
