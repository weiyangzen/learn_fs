# File Research: sources/os/linux/linux/fs/jfs/Makefile

## Purpose
Builds the Linux JFS filesystem object from its component source files.

## Build Rules
- `obj-$(CONFIG_JFS_FS) += jfs.o` builds JFS when enabled.
- `jfs-y` links core components: superblock, file/inode/namei, mount/unmount, xtree/imap/dmap/dtree, unicode, metapage, log/transaction managers, resize, xattr, ioctl, symlink, and extent code.
- `jfs-$(CONFIG_JFS_POSIX_ACL) += acl.o` includes ACL support only when configured.

## Dependencies Reflected
- `jfs_dmap.o`, `jfs_discard.o`, `inode.o`, `file.o`, `ioctl.o`, and `acl.o` in this group are part of the same `jfs.o` module.
