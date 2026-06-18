# File Research: sources/os/linux/linux/fs/ext2/acl.h

Read status: complete, 73 lines.

This header defines the ext2 ACL xattr disk format and compile-time ACL integration points.

Key responsibilities:
- Defines `EXT2_ACL_VERSION`.
- Defines disk ACL structures: `ext2_acl_entry`, `ext2_acl_entry_short`, and `ext2_acl_header`.
- Provides `ext2_acl_size()` and `ext2_acl_count()` helpers for converting between ACL entry count and serialized size.
- Declares ACL functions when `CONFIG_EXT2_FS_POSIX_ACL` is enabled.
- Provides null/no-op ACL integration when POSIX ACL support is disabled.

Research notes:
- The size/count helpers encode the disk-format distinction between the first four short ACL entries and subsequent full entries.
- When ACL support is disabled, VFS inode operation hooks resolve to `NULL`, and new inode ACL initialization succeeds as a no-op.
