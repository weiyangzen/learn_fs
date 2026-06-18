# File Research: sources/os/linux/linux-stable/fs/btrfs/direct-io.h

This header declares the Btrfs direct I/O interface.

Public API:
- Initialization:
  - `btrfs_init_dio()`
  - `btrfs_destroy_dio()`
- File operations:
  - `btrfs_direct_write()`
  - `btrfs_direct_read()`

Forward declarations:
- `struct kiocb`
- `struct iov_iter` is used by prototypes through included kernel type context.

Role in Btrfs:
The header exposes direct read/write entry points and bioset lifecycle hooks to the broader filesystem code.
