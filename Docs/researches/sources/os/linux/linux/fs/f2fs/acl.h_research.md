# File Research: sources/os/linux/linux/fs/f2fs/acl.h

## Purpose
Defines F2FS POSIX ACL on-disk structures and function declarations.

## Key Definitions
- `F2FS_ACL_VERSION` is `0x0001`.
- `f2fs_acl_header` stores ACL version.
- `f2fs_acl_entry_short` stores tag and permission for entries without ids.
- `f2fs_acl_entry` stores tag, permission, and user/group id.

## Conditional API
When `CONFIG_F2FS_FS_POSIX_ACL` is enabled, declares `f2fs_get_acl()`, `f2fs_set_acl()`, and `f2fs_init_acl()`. Otherwise get/set are `NULL` and init is a no-op.
