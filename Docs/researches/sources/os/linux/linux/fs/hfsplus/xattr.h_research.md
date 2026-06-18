# File Research: sources/os/linux/linux/fs/hfsplus/xattr.h

Purpose: Declares the HFS+ xattr handler interface shared by the core xattr implementation and per-namespace handler files.

Key declarations:
- Extern handler objects for OS X, user, trusted, and security namespaces.
- `hfsplus_xattr_handlers[]` exported handler table.
- Core internal and prefixed get/set APIs: `__hfsplus_setxattr()`, `hfsplus_setxattr()`, `__hfsplus_getxattr()`, `hfsplus_getxattr()`.
- `hfsplus_listxattr()` for VFS listxattr.
- `hfsplus_init_security()` for security label initialization during inode creation.

Dependencies and integration:
- Includes Linux xattr definitions and is consumed by HFS+ inode/directory creation and all xattr namespace files.

Risk notes:
- The header exposes both raw full-name APIs and prefix-composing APIs; callers must choose the correct layer to avoid duplicate prefixes.
