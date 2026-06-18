# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metadir.h

## Role
`xfs_metadir.h` declares the metadata directory update object and APIs for loading, creating, linking, committing, canceling, and making metadata directory entries.

## Main Definition
- `struct xfs_metadir_update` stores the metadata parent directory, path component, parent pointer args, child inode, transaction, metadata file type, and lock-state bits.

## Exported API
- Lookup/load: `xfs_metadir_load`.
- Create workflow: `xfs_metadir_start_create` and `xfs_metadir_create`.
- Link workflow: `xfs_metadir_start_link` and `xfs_metadir_link`.
- Transaction completion: `xfs_metadir_commit` and `xfs_metadir_cancel`.
- Convenience directory creation: `xfs_metadir_mkdir`.

## Dependencies
The header depends on inode, transaction, parent pointer, and metadata file type definitions from surrounding XFS headers.

## Research Notes
This header models metadata directory mutations as explicit begin/change/commit-or-cancel workflows so callers can finish inode-specific initialization before releasing resources.
