# File Research: sources/os/linux/linux/fs/ext4/xattr_hurd.c

## Purpose
Provides the ext4 xattr handler for GNU/Hurd-prefixed extended attributes.

## Behavior
- Uses prefix `XATTR_HURD_PREFIX`.
- Lists, gets, and sets only when the filesystem has `XATTR_USER` mount option enabled.
- Maps all operations to `EXT4_XATTR_INDEX_HURD` through `ext4_xattr_get()` and `ext4_xattr_set()`.

## Integration
Registered as `ext4_xattr_hurd_handler`, included in ext4 handler arrays unconditionally.
