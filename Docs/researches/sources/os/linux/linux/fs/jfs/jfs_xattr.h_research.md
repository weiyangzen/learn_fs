# File Research: sources/os/linux/linux/fs/jfs/jfs_xattr.h

Defines JFS extended attribute on-disk list structures and xattr/security entry points.

On-disk structures:
- `struct jfs_ea` stores one attribute with flag, name length, little-endian value length, and a flexible name field. The name includes a null terminator for OS/2 compatibility; the value follows immediately.
- `struct jfs_ea_list` stores total list size followed by packed `jfs_ea` entries.

Macros:
- `MAXEASIZE` and `MAXEALISTSIZE` cap EA storage at 65535 bytes.
- `EA_SIZE`, `NEXT_EA`, `FIRST_EA`, `EALIST_SIZE`, and `END_EALIST` walk packed EA lists.

Exports:
- `__jfs_setxattr`, `__jfs_getxattr`, `jfs_listxattr`.
- `jfs_xattr_handlers`.
- `jfs_init_security()` when `CONFIG_JFS_SECURITY` is enabled, otherwise a no-op inline.

Integration:
- Transaction-aware xattr updates receive a `tid_t`, tying EA storage changes into JFS commit and map update machinery.
