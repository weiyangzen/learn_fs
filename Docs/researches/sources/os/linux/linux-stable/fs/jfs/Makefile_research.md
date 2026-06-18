# File Research: sources/os/linux/linux-stable/fs/jfs/Makefile

Builds the JFS kernel module/object.

Composition:
- `obj-$(CONFIG_JFS_FS) += jfs.o`.
- Core `jfs-y` includes superblock, file/inode/namei, mount/unmount, xtree/dtree/imap/dmap, unicode, discard, extent, symlink, metapage, log/transaction manager, resize, xattr, and ioctl code.
- `acl.o` is included only when `CONFIG_JFS_POSIX_ACL` is enabled.

Integration:
- Confirms files in this group are part of the main JFS object, except ACL is feature-gated.
