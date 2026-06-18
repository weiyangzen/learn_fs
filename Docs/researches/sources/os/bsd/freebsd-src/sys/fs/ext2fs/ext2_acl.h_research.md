# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_acl.h

Read completely: 55 lines.

Purpose: declares ext2/ext4 ACL disk structures and VOP helper prototypes.

Key definitions:
- `EXT4_ACL_VERSION` is `0x0001`.
- `struct ext2_acl_entry` stores tag, permission, and id for user/group ACL entries.
- `struct ext2_acl_entry_short` stores only tag and permission for entries that do not carry an id.
- `struct ext2_acl_header` stores the ACL version.

Exported functions:
- `ext2_sync_acl_from_inode()`.
- `ext2_getacl()`.
- `ext2_setacl()`.
- `ext2_aclcheck()`.

Research notes:
- This header is intentionally small and tied to `ext2_acl.c`.
- It models ext4 ACL xattr layout rather than native UFS ACL storage.
