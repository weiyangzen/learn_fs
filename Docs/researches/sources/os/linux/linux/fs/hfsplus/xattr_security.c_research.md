# File Research: sources/os/linux/linux/fs/hfsplus/xattr_security.c

Purpose: Implements the HFS+ `security.*` xattr namespace and security label initialization hook.

Key functions:
- `hfsplus_security_getxattr()` reads `security.*` attributes through `hfsplus_getxattr()`.
- `hfsplus_security_setxattr()` writes `security.*` attributes through `hfsplus_setxattr()`.
- `hfsplus_initxattrs()` receives LSM-provided initial security xattrs, prefixes them with `security.`, and stores them via `__hfsplus_setxattr()`.
- `hfsplus_init_security()` calls `security_inode_init_security()` with the HFS+ initializer callback.

Dependencies and integration:
- Uses Linux security/xattr APIs and the shared HFS+ xattr core.
- Exported as `hfsplus_xattr_security_handler`.

Risk notes:
- Initial xattr name allocation uses the HFS+ max expanded attribute-name size and concatenates prefix plus LSM name.
- Empty security xattr names are skipped during initialization.
