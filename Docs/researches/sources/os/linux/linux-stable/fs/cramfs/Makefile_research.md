# File Research: sources/os/linux/linux-stable/fs/cramfs/Makefile

This file defines CramFs build composition.

Key responsibilities:
- Builds `cramfs.o` when `CONFIG_CRAMFS` is enabled.
- Composes it from `inode.o` and `uncompress.o`.

Dependencies:
- `inode.o` contains VFS/mount/read logic.
- `uncompress.o` wraps zlib inflate support.
