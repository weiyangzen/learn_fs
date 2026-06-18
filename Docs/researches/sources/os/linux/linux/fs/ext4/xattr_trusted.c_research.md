# File Research: sources/os/linux/linux/fs/ext4/xattr_trusted.c

## Purpose
Provides ext4 support for `trusted.*` extended attributes.

## Behavior
- Uses prefix `XATTR_TRUSTED_PREFIX`.
- Listing is restricted to callers with `CAP_SYS_ADMIN`.
- Get/set map to `EXT4_XATTR_INDEX_TRUSTED`.

## Integration
Registered as `ext4_xattr_trusted_handler` and included in ext4 handler arrays.
