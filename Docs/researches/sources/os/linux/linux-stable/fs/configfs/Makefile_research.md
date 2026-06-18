# File Research: sources/os/linux/linux-stable/fs/configfs/Makefile

This file defines how configfs is built.

Key responsibilities:
- Builds `configfs.o` when `CONFIG_CONFIGFS_FS` is enabled.
- Composes `configfs.o` from `inode.o`, `file.o`, `dir.o`, `symlink.o`, `mount.o`, and `item.o`.

Dependencies:
- Mirrors the functional split of configfs into mount setup, inode/dentry helpers, directory object lifecycle, file attributes, symlinks, and generic item reference handling.

Risks and invariants:
- All listed objects are required for the configfs module/built-in object.
