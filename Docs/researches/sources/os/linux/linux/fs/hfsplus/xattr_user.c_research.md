# File Research: sources/os/linux/linux/fs/hfsplus/xattr_user.c

Purpose: Implements the HFS+ `user.*` xattr namespace handler.

Key functions:
- `hfsplus_user_getxattr()` delegates reads to `hfsplus_getxattr()` with `XATTR_USER_PREFIX`.
- `hfsplus_user_setxattr()` delegates writes/removals to `hfsplus_setxattr()` with the user prefix.

Dependencies and integration:
- Shares all storage behavior with `xattr.c`.
- Exported as `hfsplus_xattr_user_handler`.

Risk notes:
- This handler is intentionally thin; validation and HFS+ storage limitations are enforced by the shared core.
