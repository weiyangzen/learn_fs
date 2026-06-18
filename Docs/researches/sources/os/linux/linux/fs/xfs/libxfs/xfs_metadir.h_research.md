# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_metadir.h

This header defines the metadata directory update state and declares metadata directory operations.

Key contents:
- `struct xfs_metadir_update`, carrying:
  - parent directory inode
  - path component
  - parent-pointer args
  - child metadata inode
  - transaction
  - metadata file type
  - lock-state booleans
- Prototypes for:
  - `xfs_metadir_load`
  - `xfs_metadir_start_create`
  - `xfs_metadir_create`
  - `xfs_metadir_start_link`
  - `xfs_metadir_link`
  - `xfs_metadir_commit`
  - `xfs_metadir_cancel`
  - `xfs_metadir_mkdir`

Integration:
- Used by metadir-aware metadata inode creation/loading code, quota inode helpers, realtime metadata file setup, and repair/tools code.

Risk notes:
- The update struct encodes ownership of transaction and inode locks; callers must follow start/create-or-link/commit-or-cancel sequencing.
- `metafile_type` is used to stamp and later validate metadata inodes.
