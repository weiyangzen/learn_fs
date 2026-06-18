# File Research: sources/os/linux/linux/fs/xfs/xfs_export.h

Defines XFS export/NFS filehandle formats and the exported inode lookup helper.

Key contents:
- Detailed comments describe five fileid encodings, including 32-bit and 64-bit inode-number variants with optional parent identity.
- `struct xfs_fid64` packs inode, generation, parent inode, and parent generation for 64-bit inode filehandles.
- `XFS_FILEID_TYPE_64FLAG` marks 64-bit inode filehandle formats and is wire-visible.
- Declares `xfs_nfs_get_inode`.

The header documents an important operational caveat: 64-bit inode exports interact poorly with NFS fsid fields unless exporting the mountpoint or using an explicit `fsid`.
