# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_export.c

## Purpose

Implements XFS exportfs operations for NFS and pNFS-style file handle use. It encodes XFS inode identities into file handles and decodes handles back into dentries/inodes.

## Main Responsibilities

- Chooses file handle format and length based on:
  - 32-bit versus 64-bit inode support
  - whether parent information is requested
- Encodes file handles in `xfs_fs_encode_fh`.
- Resolves NFS handles to inodes through `xfs_nfs_get_inode`.
- Converts file handles to dentries or parent dentries:
  - `xfs_fs_fh_to_dentry`
  - `xfs_fs_fh_to_parent`
- Looks up a directory parent through `..` in `xfs_fs_get_parent`.
- Forces inode metadata for NFS commit through `xfs_fs_nfs_commit_metadata`.
- Exposes `xfs_export_operations`.

## Important Invariants

- Generation zero is valid in XFS, so fileid lengths must be explicit; missing parent generation cannot default to zero.
- Inode number zero is rejected as stale.
- `XFS_IGET_UNTRUSTED` is used because clients can send arbitrary or stale file handles.
- Invalid, missing, or corrupt inode clusters are translated to `-ESTALE` for NFS semantics.
- Private/internal inodes are not exported.

## Dependencies

- Uses `xfs_iget` and inode generation checks for stable handle resolution.
- Uses `xfs_inode_reload_unlinked` if an unlinked inode's incore list is incomplete.
- Optionally wires pNFS block operations under `CONFIG_EXPORTFS_BLOCK_OPS`.

## Research Notes

This file bridges XFS inode identity with VFS exportfs. It is careful to treat corrupt or gone inode locations as stale handles rather than ordinary filesystem corruption in the NFS path.
