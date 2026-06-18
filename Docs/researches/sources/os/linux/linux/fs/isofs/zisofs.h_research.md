# File Research: sources/os/linux/linux/fs/isofs/zisofs.h

Small header for optional zisofs decompression support.

When `CONFIG_ZISOFS` is enabled, it declares:
- `zisofs_aops`
- `zisofs_init()`
- `zisofs_cleanup()`

Included by ISOFS inode and compression code to connect compressed file address-space operations and module lifecycle.
