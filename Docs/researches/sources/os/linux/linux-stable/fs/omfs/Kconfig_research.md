# File Research: sources/os/linux/linux-stable/fs/omfs/Kconfig

## Scope

This file defines the kernel configuration option for OMFS, the SonicBlue Optimized MPEG File System used by Rio Karma and ReplayTV devices.

## Behavior

- `config OMFS_FS` is a tristate option named “SonicBlue Optimized MPEG File System support”.
- It depends on block-device support.
- It selects `BUFFER_HEAD` and `CRC_ITU_T`, matching OMFS use of buffer-head I/O and on-disk CRC checksums.
- Help text documents the historical devices, warns the filesystem is not actually more efficient for MPEG files, and names the module `omfs`.

## Dependencies

- Build-time dependency is `BLOCK`.
- Selected helpers are required by `inode.c` and related OMFS code.
