# File Research: sources/os/linux/linux/fs/ext2/acl.c

Read status: complete, 276 lines.

This file implements ext2 POSIX ACL support on top of ext2 extended attributes.

Key responsibilities:
- Converts ACL xattr bytes from disk format to in-memory `struct posix_acl` via `ext2_acl_from_disk()`.
- Converts in-memory ACLs to ext2 disk xattr format via `ext2_acl_to_disk()`.
- Loads access/default ACLs with `ext2_get_acl()`.
- Stores or removes ACLs through `__ext2_set_acl()` and `ext2_set_acl()`.
- Initializes inherited ACLs for new inodes with `ext2_init_acl()`.

Important data/control flow:
- Access ACLs use `EXT2_XATTR_INDEX_POSIX_ACL_ACCESS`.
- Default ACLs use `EXT2_XATTR_INDEX_POSIX_ACL_DEFAULT` and are only valid for directories.
- `ext2_set_acl()` updates inode mode through `posix_acl_update_mode()` for access ACL changes, then marks the inode dirty if mode changed.
- `ext2_init_acl()` uses `posix_acl_create()` to derive default/access ACLs from the parent and stores them on the new inode.

Safety and validation:
- Disk ACL parser validates header size, ACL version, entry count, entry bounds, tag type, and exact buffer consumption.
- Unknown ACL tags fail with `-EINVAL`.
- RCU ACL lookup is unsupported and returns `-ECHILD`.
- Missing xattrs map to no ACL rather than an error.

External dependencies:
- Depends on ext2 xattr get/set helpers.
- Uses Linux POSIX ACL helpers and init user namespace UID/GID conversion.

Research notes:
- ACLs are not stored in the inode proper; they are serialized as xattrs.
- The disk format has compact short entries for owner/group/mask/other and full entries for named users/groups.
