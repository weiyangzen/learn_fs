# File Research: sources/local-fs/xfsprogs/libxfs/xfs_metadir.h

## Role

This header declares the metadata directory update context and metadir operations for loading, creating, linking, committing, canceling, and creating metadata directories.

## Main Contents

`struct xfs_metadir_update` carries:

- parent directory inode
- path component
- parent pointer args
- child metadata inode
- transaction
- metadata file type
- lock state for parent and child

Declared functions cover:

- `xfs_metadir_load`
- `xfs_metadir_start_create`
- `xfs_metadir_create`
- `xfs_metadir_start_link`
- `xfs_metadir_link`
- `xfs_metadir_commit`
- `xfs_metadir_cancel`
- `xfs_metadir_mkdir`

## Dependencies

The API depends on metadata file types, transactions, inodes, mode values, and parent pointer contexts.

## Research Notes

This is a stateful API: callers own `xfs_metadir_update` and must pair start/create/link with commit or cancel to release locks and resources.
