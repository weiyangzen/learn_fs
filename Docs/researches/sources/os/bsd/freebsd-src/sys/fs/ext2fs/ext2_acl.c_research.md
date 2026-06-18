# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_acl.c

Read completely: 526 lines.

Purpose: implements ext2/ext4 POSIX.1e ACL support, guarded by `UFS_ACL`, converting between FreeBSD in-memory ACLs and ext4-compatible on-disk extended-attribute ACL format.

Key functions:
- `ext2_sync_acl_from_inode()` updates ACL entries from inode mode bits, handling `ACL_MASK` versus `ACL_GROUP_OBJ`.
- `ext2_sync_inode_from_acl()` updates inode mode from ACL permissions while preserving non-permission bits.
- `ext4_acl_from_disk()` validates ext4 ACL header/version, computes entry count, parses short and full entries, validates bounds, and fills `struct acl`.
- `ext2_getacl_posix1e()` maps ACL type to extattr namespace/name, reads the extended attribute, synthesizes minimal access/default ACLs for `ENOATTR`, decodes disk ACLs, and syncs access ACL mode bits from inode.
- `ext2_getacl()` rejects unsupported mount modes and NFSv4 ACL requests, then delegates to POSIX.1e get.
- `ext4_acl_to_disk()` computes disk size, writes ext4 ACL header and short/full entries.
- `ext2_setacl_posix1e()` validates ACLs, authorizes mutation, rejects readonly/immutable/append-only targets, writes/removes ACL extattrs, maps missing extattrs to `EOPNOTSUPP`, updates inode mode for access ACLs, calls `ext2_update()`, and sends `NOTE_ATTRIB`.
- `ext2_setacl()` gates mount ACL support and NFSv4 ACL requests.
- `ext2_aclcheck()` validates ACL type/object applicability and calls `acl_posix1e_check()`.

Important behavior:
- Access ACL deletion is rejected; default ACL deletion is allowed only on directories.
- ACL storage uses extattr names `POSIX1E_ACL_ACCESS_EXTATTR_NAME` and `POSIX1E_ACL_DEFAULT_EXTATTR_NAME`.
- Disk ACL entries omit `ae_id` for user/group object, mask, and other entries.

Research notes:
- The file bridges FreeBSD ACL VOPs to Linux/ext4-style ACL xattrs.
- A likely minor bug exists in `ext2_getacl_posix1e()`: `value` is allocated with `M_ACL` but freed with `M_TEMP` in `out`.
