# File Research: sources/os/linux/linux/fs/btrfs/fiemap.h

Read completely: 11 lines.

This header declares the Btrfs FIEMAP entry point:

- `btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo, u64 start, u64 len)`

It includes `<linux/fiemap.h>` and wraps the declaration with a standard include guard.

Important interactions:
- Implemented by `fiemap.c`.
- Exported to Btrfs inode/file operation code that wires FIEMAP into VFS ioctl handling.

Risk and correctness notes:
- The header is only an interface declaration; all behavioral complexity is in `fiemap.c`.
