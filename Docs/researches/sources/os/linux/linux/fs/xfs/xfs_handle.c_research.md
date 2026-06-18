# File Research: sources/os/linux/linux/fs/xfs/xfs_handle.c

Implements XFS handle-based ioctls: path/fd to handle, open/readlink by handle, legacy attr list/multi operations by handle, and parent-pointer retrieval.

Key logic:
- Handle construction:
  - `xfs_filehandle_init` and `xfs_fshandle_init` fill filesystem and file handles from fixed fsid, inode number, and generation.
  - `xfs_find_handle` supports path-to-fshandle, fd-to-handle, and path-to-handle, requiring XFS regular/dir/symlink targets.
- Handle lookup/open:
  - `xfs_khandle_to_dentry` decodes a copied handle through exportfs under a directory file.
  - `xfs_khandle_to_inode` retrieves an inode directly via `xfs_nfs_get_inode`, avoiding exportfs dentry tree reconstruction.
  - `xfs_handle_to_dentry` copies userspace handle data and decodes it.
  - `xfs_open_by_handle` requires `CAP_SYS_ADMIN`, restricts to regular files/directories, checks append/immutable/write rules, opens via `dentry_open`, and suppresses atime/cmtime for regular files.
  - `xfs_readlink_by_handle` requires symlink target and copies link text to userspace.
- Attribute list/multi:
  - `xfs_ioc_attr_list` validates namespace flags and cursor, uses an internal buffer, and formats legacy `xfs_attrlist` entries through `xfs_ioc_attr_put_listent`.
  - `xfs_attrlist_by_handle` lists attrs for a handle target.
  - `xfs_ioc_attrmulti_one` handles get/set/remove operations with namespace filtering and mount write protection for mutating operations.
  - `xfs_attrmulti_by_handle` copies a bounded operation array, applies each operation, stores per-op errors, and copies results back.
- Parent pointers:
  - `xfs_getparents_put_listent` filters parent-pointer attrs, decodes parent ino/gen/name, marks inode parent sickness on corruption, and formats `xfs_getparents_rec` records.
  - `xfs_getparents` validates buffer/flags/cursor, allocates an internal records buffer, iterates parent attrs, expands the last record to fill remaining buffer space, updates cursor and output flags, and copies records out.
  - `xfs_ioc_getparents` retrieves parents of the current file.
  - `xfs_ioc_getparents_by_handle` retrieves parents of a file identified by handle without exportfs path reconstruction.

The file is privilege-sensitive. Most handle operations require `CAP_SYS_ADMIN`, validate handle size/generation, and avoid copying to userspace while internal iteration state is unstable.
