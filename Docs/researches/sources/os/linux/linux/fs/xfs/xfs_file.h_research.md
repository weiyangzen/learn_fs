# File Research: sources/os/linux/linux/fs/xfs/xfs_file.h

Small public header for XFS file operations.

Key contents:
- Declares `xfs_file_operations` and `xfs_dir_file_operations`.
- Declares `xfs_is_falloc_aligned`, used by fallocate/range operations that must respect filesystem allocation units.

This is the VFS-facing declaration point for XFS regular and directory file operation tables.
