# File Research: sources/os/linux/linux-stable/fs/ext4/acl.h

## Purpose

Defines ext4 ACL on-disk structures, sizing helpers, and conditional ACL API declarations.

## Main Definitions

- `EXT4_ACL_VERSION`
- `ext4_acl_entry`: tag, permission, and id for named ACL entries.
- `ext4_acl_entry_short`: tag and permission for entries without ids.
- `ext4_acl_header`: ACL format version.

## Helpers

- `ext4_acl_size(count)` computes serialized ACL size.
- `ext4_acl_count(size)` computes ACL entry count from serialized size and rejects misaligned/malformed sizes.

## Conditional API Surface

When `CONFIG_EXT4_FS_POSIX_ACL` is enabled:

- Declares `ext4_get_acl()`.
- Declares `ext4_set_acl()`.
- Declares `ext4_init_acl()`.

When disabled:

- `ext4_get_acl` and `ext4_set_acl` are `NULL`.
- `ext4_init_acl()` is an inline no-op.

## Dependencies

- Includes `<linux/posix_acl_xattr.h>`.
- The enabled API references ext4 journal handles and inodes.

## Research Notes

The header’s size/count helpers encode ext4’s compact ACL disk format where the first four common ACL entries can omit ids. This format detail is central to validation in `acl.c`.
