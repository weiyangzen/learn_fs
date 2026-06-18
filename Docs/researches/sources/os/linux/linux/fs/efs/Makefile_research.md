# File Research: sources/os/linux/linux/fs/efs/Makefile

Builds the EFS filesystem module.

Key behavior:
- Adds `efs.o` when `CONFIG_EFS_FS` is enabled.
- Links `super.o`, `inode.o`, `namei.o`, `dir.o`, `file.o`, and `symlink.o`.

Important interactions:
- The module is organized around read-only VFS operations plus extent mapping.
