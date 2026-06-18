# File Research: sources/os/linux/linux/fs/ufs/file.c

Purpose: regular file operation table for UFS.

Key contents:
- `ufs_file_operations` mostly delegates to generic buffered file helpers:
  - llseek, read/write iterators, mmap preparation, open, fsync, splice read/write, and lease handling.

Integration:
- Installed for regular files by `ufs_set_inode_ops()` in `inode.c`.
- Uses UFS address-space operations for actual block mapping and I/O.

Risks and invariants:
- Behavior is primarily inherited from generic VFS/page-cache code; filesystem-specific mapping lives in `inode.c`.
