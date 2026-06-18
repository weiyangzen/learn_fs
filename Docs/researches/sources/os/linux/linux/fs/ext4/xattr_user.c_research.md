# File Research: sources/os/linux/linux/fs/ext4/xattr_user.c

## Purpose
Provides ext4 support for `user.*` extended attributes.

## Behavior
- Uses prefix `XATTR_USER_PREFIX`.
- List/get/set are enabled only when the ext4 `XATTR_USER` mount option is set.
- Get/set map to `EXT4_XATTR_INDEX_USER`.

## Integration
Registered as `ext4_xattr_user_handler` and included in ext4 handler arrays.
