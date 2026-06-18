# File Research: sources/os/linux/linux/fs/Makefile

Defines build composition for Linux VFS core and filesystem directories.

Key behavior:
- Builds core VFS objects unconditionally, including open/read/write paths, superblocks, dentries, inodes, namespace, fs context/parser, xattrs, sync, splice, mount idmapping, and related helpers.
- Adds optional core objects based on config, such as buffer heads, proc namespace, legacy direct I/O, epoll, signalfd, eventfd, aio, DAX, file locking, binfmt handlers, POSIX ACLs, and NFS common code.
- Adds core subdirectories including notify, iomap, quota, proc, kernfs, sysfs, configfs, devpts, dlm, netfs, ramfs, unicode, and many filesystems.
- Maps specific filesystem config symbols to directories:
  - `CONFIG_ADFS_FS` -> `adfs/`
  - `CONFIG_AFFS_FS` -> `affs/`
  - `CONFIG_9P_FS` -> `9p/`
- Preserves ordering notes, such as ext4 before ext2.

Important interactions:
- This is the build-side counterpart of `fs/Kconfig`.
- The requested ADFS, AFFS, and 9p trees are all pulled into the kernel build through this file.
