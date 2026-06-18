# File Research: sources/os/linux/linux/fs/9p/xattr.h

Declares 9p extended attribute interfaces.

Key behavior:
- Exposes `v9fs_xattr_handlers` for superblock installation.
- Declares FID-based and dentry-based xattr get/set helpers.
- Declares `v9fs_listxattr()`.

Important interactions:
- Used by dotl inode operations and superblock setup.
- Depends on 9p client xattr RPC support.
