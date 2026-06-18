# File Research: sources/os/linux/linux-stable/fs/hfsplus/xattr_trusted.c

## Purpose

Implements the `trusted.*` HFS+ xattr namespace handler.

## Main Entry Points

- `hfsplus_trusted_getxattr()`
- `hfsplus_trusted_setxattr()`
- `hfsplus_xattr_trusted_handler`

## Control Flow And Dependencies

The callbacks simply prepend `XATTR_TRUSTED_PREFIX` through the shared `hfsplus_getxattr()` and `hfsplus_setxattr()` helpers. Visibility filtering for `trusted.*` is handled in the core list function.

## Risks

The file relies entirely on VFS-level namespace permission handling plus the core HFS+ `can_list()` behavior. There is no local validation beyond passing the trusted prefix.
