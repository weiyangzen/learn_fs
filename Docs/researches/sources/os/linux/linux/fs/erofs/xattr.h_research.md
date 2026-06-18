# File Research: sources/os/linux/linux/fs/erofs/xattr.h

## Purpose
Declares the EROFS xattr, POSIX ACL, no-ACL filter, and inode-share fingerprint interfaces used by the rest of the EROFS filesystem.

## Main Elements
- Includes `internal.h`, POSIX ACL xattr declarations, and generic Linux xattr declarations.
- When `CONFIG_EROFS_FS_XATTR` is enabled, declares `erofs_xattr_handlers`, `erofs_xattr_prefixes_init()`, `erofs_xattr_prefixes_cleanup()`, and `erofs_listxattr()`.
- When xattrs are disabled, provides no-op cleanup/init stubs and NULL-style macros for listxattr and xattr handlers.
- When POSIX ACLs are enabled, declares `erofs_get_acl()`; otherwise it maps the ACL getter to NULL.
- Always declares `erofs_xattr_fill_inode_fingerprint()` and `erofs_inode_has_noacl()` for optional call sites that may have configuration-specific definitions or stubs elsewhere.

## Dependencies And Integration
This header is consumed by `super.c`, inode operations, and xattr-related EROFS code to wire VFS xattr handlers and ACL hooks according to Kconfig.

## Risk Notes
Configuration stubs must stay type-compatible with call sites. The always-declared fingerprint and no-ACL helpers require matching definitions or configuration-provided inline behavior elsewhere in the EROFS internal headers.
