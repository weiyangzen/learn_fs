# File Research: sources/os/linux/linux/fs/jffs2/acl.c

## Role

`acl.c` implements JFFS2 POSIX ACL support on top of JFFS2 extended attributes. It converts ACLs between Linux `struct posix_acl` and the compact JFFS2 on-flash ACL format, reads and writes ACL xattrs, updates inode mode bits for access ACLs, and initializes inherited ACLs during inode creation.

## On-Flash ACL Encoding

The file supports:
- `struct jffs2_acl_header` with `JFFS2_ACL_VERSION`.
- Short entries for `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, `ACL_MASK`, and `ACL_OTHER`.
- Full entries with id fields for named `ACL_USER` and `ACL_GROUP`.

Helpers:
- `jffs2_acl_size()` computes serialized size.
- `jffs2_acl_count()` validates serialized size and computes entry count.
- `jffs2_acl_from_medium()` parses flash/xattr bytes into a `posix_acl`.
- `jffs2_acl_to_medium()` serializes a `posix_acl` into JFFS2 byte order.

## ACL Read Path

`jffs2_get_acl()`:
- Rejects RCU ACL lookup with `-ECHILD`.
- Maps `ACL_TYPE_ACCESS` to `JFFS2_XPREFIX_ACL_ACCESS`.
- Maps `ACL_TYPE_DEFAULT` to `JFFS2_XPREFIX_ACL_DEFAULT`.
- Uses `do_jffs2_getxattr()` first to determine size, then to read the value.
- Returns `NULL` for absent ACL xattrs (`-ENODATA` or `-ENOSYS`) and parsed ACLs otherwise.

## ACL Write Path

`__jffs2_set_acl()` serializes an ACL and writes it through `do_jffs2_setxattr()`. A NULL ACL removes the xattr and treats missing xattrs as success.

`jffs2_set_acl()` handles VFS ACL updates:
- For access ACLs, calls `posix_acl_update_mode()` and updates inode mode/ctime through `jffs2_do_setattr()` when required.
- For default ACLs, rejects non-directory targets with `-EACCES` when an ACL is being set.
- Updates the inode ACL cache with `set_cached_acl()` after a successful write.

## Inode Creation ACL Initialization

`jffs2_init_acl_pre()`:
- Initializes inode ACL cache state.
- Calls `posix_acl_create()` to compute inherited default/access ACLs and adjusted mode.
- Stores inherited ACLs temporarily in inode cache fields.

`jffs2_init_acl_post()`:
- Writes cached default and access ACLs to xattrs after the inode has been created on flash.

This two-stage pattern lets JFFS2 apply ACL-derived mode during inode creation while writing ACL xattrs only after the new inode exists.

## Important Invariants

- ACL version must match `JFFS2_ACL_VERSION`.
- Serialized sizes must exactly match the expected short/full entry layout.
- Named user/group ids are converted through `init_user_ns`.
- Default ACLs are valid only on directories.
- Access ACL mode changes must be persisted through JFFS2 setattr before writing the ACL xattr.

## Research Notes

The file is a thin but important adapter between Linux POSIX ACL APIs and JFFS2’s xattr subsystem. The main risk areas are serialized ACL validation, exact size accounting, id mapping, and keeping inode mode bits consistent with access ACLs.
