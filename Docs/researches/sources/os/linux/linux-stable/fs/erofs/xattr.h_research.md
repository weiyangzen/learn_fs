# File Research: sources/os/linux/linux-stable/fs/erofs/xattr.h

This header declares EROFS xattr and ACL integration points used by the rest of the filesystem.

Primary contents:
- Includes EROFS internals plus Linux POSIX ACL xattr and generic xattr declarations.
- When `CONFIG_EROFS_FS_XATTR` is enabled, declares:
  - `erofs_xattr_handlers`
  - `erofs_xattr_prefixes_init()`
  - `erofs_xattr_prefixes_cleanup()`
  - `erofs_listxattr()`
- When xattrs are disabled, provides no-op prefix init/cleanup and maps `erofs_listxattr` and `erofs_xattr_handlers` to `NULL`.
- When `CONFIG_EROFS_FS_POSIX_ACL` is enabled, declares `erofs_get_acl()`; otherwise maps it to `NULL`.
- Declares inode-share and ACL-filter helpers:
  - `erofs_xattr_fill_inode_fingerprint()`
  - `erofs_inode_has_noacl()`

Design role:
- Lets `super.c` always wire `sb->s_xattr` and inode ACL operations through configuration-safe symbols.
- Keeps feature-dependent VFS hooks centralized, so callers do not need to duplicate xattr/ACL `#ifdef` logic.
