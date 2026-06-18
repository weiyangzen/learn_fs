# File Research: sources/os/linux/linux-stable/fs/ext2/Makefile

## Summary
Defines the ext2 built object composition.

## Main Contents
- Builds `ext2.o` when `CONFIG_EXT2_FS` is enabled.
- Core objects: `balloc.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `ioctl.o`, `namei.o`, `super.o`, `symlink.o`, `trace.o`.
- Adds `xattr.o`, `xattr_user.o`, and `xattr_trusted.o` for `CONFIG_EXT2_FS_XATTR`.
- Adds `acl.o` for `CONFIG_EXT2_FS_POSIX_ACL`.
- Adds `xattr_security.o` for `CONFIG_EXT2_FS_SECURITY`.
- Adds `-I$(src)` for tracepoint compilation.

## Risks
The build layout mirrors feature dependencies from Kconfig. ACL and security behavior disappear entirely when their config symbols are off.
