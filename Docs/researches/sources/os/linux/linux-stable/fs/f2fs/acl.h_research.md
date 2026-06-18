# File Research: sources/os/linux/linux-stable/fs/f2fs/acl.h

## Purpose
Declares F2FS ACL on-disk structures and ACL operation prototypes.

## Main Components
- `F2FS_ACL_VERSION` is the on-disk ACL version.
- `f2fs_acl_header` stores the version.
- `f2fs_acl_entry_short` stores tag and permission for entries without an ID.
- `f2fs_acl_entry` adds a 32-bit ID for named user/group entries.
- When `CONFIG_F2FS_FS_POSIX_ACL` is enabled, prototypes are provided for get, set, and init operations.
- When disabled, ACL get/set hooks become `NULL` and `f2fs_init_acl()` is a no-op returning success.

## Research Notes
The header defines the disk ABI for F2FS ACL xattr payloads.
