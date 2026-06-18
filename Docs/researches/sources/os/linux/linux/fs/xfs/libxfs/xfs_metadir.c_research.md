# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_metadir.c

This file implements the metadata directory tree abstraction for metadata inodes stored inside special internal directories.

Major responsibilities:
- Look up metadata files/directories by path component with `xfs_metadir_lookup`.
- Load a metadata inode with `xfs_metadir_load`.
- Start, create, link, commit, and cancel metadata directory updates.
- Create metadata directories with `xfs_metadir_mkdir`.
- Coordinate transaction allocation, inode locks, directory updates, parent-pointer context, and cleanup.

Important behavior:
- Feature-gated by `xfs_has_metadir`.
- Metadata directory entries are validated for inode number and expected file type.
- Parent directory must be an actual directory; failure marks metadir health sick.
- Creation uses `xfs_dialloc`, `xfs_icreate`, `xfs_metafile_set_iflag`, and directory child creation.
- Parent pointer update context is allocated via `xfs_parent_start` when needed.
- Metadata files are not accounted to quota.
- Kernel builds exclude `xfs_metadir_start_link` and `xfs_metadir_link` via `#ifndef __KERNEL__`.

Lifecycle model:
- Callers populate `struct xfs_metadir_update`.
- Start function allocates transaction/resources and locks parent/child as appropriate.
- Create/link performs the actual directory operation.
- Caller must finish with commit or cancel, which tears down locks and parent-pointer context.
- If create returns an inode along with an error, caller must still finish inode setup before releasing it.

Risk notes:
- Files in the metadata directory tree currently cannot be unlinked.
- Cleanup paths are important because transactions and locks are staged across multiple functions.
- Metadata directory corruption maps to filesystem health state.
