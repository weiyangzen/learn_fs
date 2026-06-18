# File Research: sources/os/linux/linux-stable/fs/jfs/file.c

Defines regular-file inode/file operations and setattr/fsync behavior.

Key functions:
- `jfs_fsync()` writes dirty page-cache range, then either flushes journal or commits dirty inode synchronously.
- `jfs_open()` initializes quotas and tracks an active allocation group for newly opened empty writable regular files to reduce fragmentation.
- `jfs_release()` decrements active AG counters.
- `jfs_setattr()` validates attribute changes, handles quota initialization/transfer, truncates on size changes, marks inode dirty, and invokes ACL chmod updates.

Exports:
- `jfs_file_inode_operations`: listxattr, setattr, fileattr get/set, optional ACL get/set.
- `jfs_file_operations`: generic read/write/mmap/splice/llseek plus JFS fsync, release, ioctl, compat ioctl, and lease handling.

Risk notes:
- `jfs_setattr()` has a latent return-value sharp edge: if no earlier operation initializes `rc` after `setattr_prepare()`, the final return relies on the earlier zero path unless chmod runs.
