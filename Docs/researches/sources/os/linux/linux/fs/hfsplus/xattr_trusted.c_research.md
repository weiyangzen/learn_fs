# File Research: sources/os/linux/linux/fs/hfsplus/xattr_trusted.c

Purpose: Implements the HFS+ `trusted.*` xattr namespace handler.

Key functions:
- `hfsplus_trusted_getxattr()` delegates reads to `hfsplus_getxattr()` with `XATTR_TRUSTED_PREFIX`.
- `hfsplus_trusted_setxattr()` delegates writes/removals to `hfsplus_setxattr()` with the trusted prefix.

Dependencies and integration:
- Shares all storage behavior with `xattr.c`.
- Exported as `hfsplus_xattr_trusted_handler`.

Risk notes:
- Permission filtering for listing trusted names is handled in the core list path, not in this small handler.
