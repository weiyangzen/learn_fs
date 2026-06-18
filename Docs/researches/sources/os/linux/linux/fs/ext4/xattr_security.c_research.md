# File Research: sources/os/linux/linux/fs/ext4/xattr_security.c

## Purpose
Provides ext4 support for `security.*` extended attributes and LSM security initialization.

## Behavior
- Maps get/set to `EXT4_XATTR_INDEX_SECURITY`.
- `ext4_init_security()` calls `security_inode_init_security()` and stores returned initial labels using `ext4_xattr_set_handle()` inside the caller-provided journal handle.
- Initial xattrs are created with `XATTR_CREATE`.

## Integration
Registered as `ext4_xattr_security_handler` when `CONFIG_EXT4_FS_SECURITY` is enabled.
