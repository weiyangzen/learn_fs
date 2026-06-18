# File Research: sources/os/linux/linux-stable/fs/ext2/acl.h

## Summary
Defines ext2 POSIX ACL on-disk structures, size/count helpers, and ACL function declarations or stubs.

## Main Contents
- `EXT2_ACL_VERSION`.
- `ext2_acl_entry`, `ext2_acl_entry_short`, and `ext2_acl_header`.
- `ext2_acl_size()` and `ext2_acl_count()`.
- Declarations for `ext2_get_acl()`, `ext2_set_acl()`, and `ext2_init_acl()` when ACL support is enabled.
- Null/no-op stubs when `CONFIG_EXT2_FS_POSIX_ACL` is disabled.

## Important Behavior
The size helpers encode the ext2 ACL storage rule: the first four base ACL entries use the short format, while named user/group entries use the full format with an ID field.

## Risks
The count helper returns `-1` for malformed payload sizes; callers must treat that as invalid on-disk ACL data.
