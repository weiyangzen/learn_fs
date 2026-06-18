# File Research: sources/os/linux/linux/fs/xfs/xfs_export.c

Implements XFS NFS/exportfs operations.

Key logic:
- `xfs_fileid_length` maps supported filehandle types to encoded word lengths and rejects invalid types.
- `xfs_fs_encode_fh` encodes inode and optional parent identity, selecting 32-bit or 64-bit inode formats depending on filesystem inode-number policy and available caller buffer space.
- `xfs_nfs_get_inode` retrieves an inode by inode number and generation with `XFS_IGET_UNTRUSTED`, translating stale/corrupt lookup errors to `ESTALE`, reloading incomplete unlinked state if needed, and rejecting generation mismatches or private inodes.
- `xfs_fs_fh_to_dentry` and `xfs_fs_fh_to_parent` decode filehandle records back into dentries.
- `xfs_fs_get_parent` resolves `..` through XFS directory lookup.
- `xfs_fs_nfs_commit_metadata` forces inode log metadata for NFS commit semantics.
- `xfs_export_operations` wires XFS into exportfs and optionally pNFS block operations.

The file’s central concern is stable cross-reboot inode identity while preserving XFS generation checks and safe handling of stale client filehandles.
