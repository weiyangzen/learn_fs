# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metadir.c

## Role
`xfs_metadir.c` implements the metadata directory abstraction for looking up, creating, linking, committing, and canceling metadata inode updates inside the special XFS metadata directory tree.

## Main Responsibilities
- Convert metadata path components into `struct xfs_name`.
- Look up metadata directory entries with directory btree/shortform machinery and verify inode/filetype results.
- Load metadata inodes by path and metatype.
- Allocate transaction and parent-pointer context for metadata directory creation/link operations.
- Create metadata files/directories and insert directory entries.
- Commit or cancel metadata directory updates while releasing locks and parent pointer resources.
- Provide a convenience mkdir wrapper for one metadata directory path component.

## Important Functions
- `xfs_metadir_lookup` performs a locked directory lookup, verifies the parent is a directory, validates returned inode number and requested file type, and marks metadata directory health sick on corruption.
- `xfs_metadir_load` looks up a path component under a metadata directory and reads it through `xfs_trans_metafile_iget`.
- `xfs_metadir_start_create` allocates parent pointer context and a create transaction, then locks the parent directory.
- `xfs_metadir_create` checks nonexistence, allocates and creates the inode, sets metadata inode flags, joins the parent directory after possible transaction roll, and creates the directory entry.
- `xfs_metadir_start_link` and `xfs_metadir_link` support userspace-only linking of an existing metadata inode into the tree.
- `xfs_metadir_commit` commits the transaction and tears down locks/resources.
- `xfs_metadir_cancel` cancels the transaction and tears down locks/resources.
- `xfs_metadir_mkdir` creates a metadata subdirectory and handles inode setup/release on commit or failure.

## Data and Invariants
- All metadata directory tree operations require the metadir feature.
- Callers synchronize metadata directory inodes with ILOCK; IOLOCK/MMAPLOCK are unnecessary because metadata inodes are not user visible.
- New metadata inodes get `XFS_DIFLAG2_METADATA` and mandatory metadata flags immediately after creation.
- The path parameter is a single metadata directory component in these helpers; ancestor directories must already exist.
- Metadata directory files are not quota-accounted.

## Error Handling and Corruption Response
- Non-directory metadata parents, invalid lookup inode numbers, and filetype mismatches mark filesystem metadata directory health sick and return `-EFSCORRUPTED`.
- Creation can return an inode even on later error; callers must finish inode setup before releasing it so cleanup can proceed correctly.
- Cancel/commit teardown frees parent pointer args and unlocks any locked parent/child inode.

## Dependencies
This file depends on directory lookup/create helpers, parent pointer update setup, inode allocation/create, metadata file flagging, transaction reservations, health reporting, and metadir feature checks.

## Research Notes
This is an abstraction layer for new metadata inodes, excluding legacy realtime bitmap/summary and quota inodes. The update object centralizes parent inode, child inode, transaction, parent-pointer args, metatype, and lock state.
