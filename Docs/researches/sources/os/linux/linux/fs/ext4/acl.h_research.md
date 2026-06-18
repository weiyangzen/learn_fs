# File Research: sources/os/linux/linux/fs/ext4/acl.h

## Purpose
Defines ext4 POSIX ACL disk structures, sizing helpers, and ACL API declarations/stubs.

## Main Responsibilities
- Defines `EXT4_ACL_VERSION`, ACL header, full entry, and short entry formats.
- `ext4_acl_size()` computes serialized ACL xattr size.
- `ext4_acl_count()` validates a serialized size and returns the number of ACL entries.
- Declares `ext4_get_acl()`, `ext4_set_acl()`, and `ext4_init_acl()` when ACL support is enabled.
- Provides null/stub behavior when `CONFIG_EXT4_FS_POSIX_ACL` is disabled.

## Integration Points
Used by `acl.c`, inode creation, and inode operation tables.

## Risks and Edge Cases
The first four ACL entries are encoded in short form unless user/group IDs are needed; sizing/count logic must stay compatible with `acl.c` parsing.
