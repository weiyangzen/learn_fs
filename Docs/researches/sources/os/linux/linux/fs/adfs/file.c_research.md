# File Research: sources/os/linux/linux/fs/adfs/file.c

Defines regular-file VFS operation tables for ADFS.

Key behavior:
- `adfs_file_operations` uses generic helpers for:
  - llseek
  - read_iter
  - mmap preparation
  - fsync
  - write_iter
  - splice_read
- `adfs_file_inode_operations` provides `setattr = adfs_setattr`.

Important interactions:
- Actual block mapping and address-space operations are implemented in `inode.c`.
- Write behavior depends on mount/write-support configuration and allocation limitations.
