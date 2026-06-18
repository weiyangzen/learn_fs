# File Research: sources/os/linux/linux/fs/affs/Kconfig

Defines configuration for Amiga Fast File System support.

Key behavior:
- `AFFS_FS` is a tristate option depending on `BLOCK`.
- Selects `BUFFER_HEAD` and `LEGACY_DIRECT_IO`.
- Help text describes read/write support for Amiga FFS partitions and disk images, excluding native Amiga floppies due to controller incompatibility.
- Module name is `affs`.

Important interactions:
- Controls inclusion of `fs/affs/` through the top-level `fs/Makefile`.
