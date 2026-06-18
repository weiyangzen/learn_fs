# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext4_acl.h

## Purpose
Defines ext4 on-disk ACL and POSIX ACL xattr structures used by xattr conversion code.

## Key Definitions
- Ext4 ACL version `EXT4_ACL_VERSION`.
- ACL tag constants: user object, user, group object, group, mask, other.
- ACL type constants: access and default.
- `ACL_UNDEFINED_ID`.
- `ext4_acl_entry`, `ext4_acl_entry_short`, `ext4_acl_header`.
- POSIX ACL xattr version `POSIX_ACL_XATTR_VERSION`.
- `posix_acl_xattr_entry`, `posix_acl_xattr_header`.

## Integration
Included by `ext_attr.c`, which converts between userspace POSIX ACL xattr format and compact ext4 on-disk ACL encoding.

## Risks and Notes
- ACL entries with no qualifier use the short on-disk form.
- The flexible `a_entries[0]` member is guarded for GCC pedantic diagnostics.
