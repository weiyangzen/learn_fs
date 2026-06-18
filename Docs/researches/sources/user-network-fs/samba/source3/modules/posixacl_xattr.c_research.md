# sources/user-network-fs/samba/source3/modules/posixacl_xattr.c

## Purpose
Implements POSIX ACL get/set/delete helpers that store Linux POSIX ACL xattr binary format directly, used by backends that expose ACLs through xattrs instead of native sys_acl calls.

## APIs, Types, And Control Flow
Public functions are `posixacl_xattr_acl_get_fd()`, `posixacl_xattr_acl_set_fd()`, and `posixacl_xattr_acl_delete_def_fd()`. The parser validates a 4-byte version, requires 8-byte entries, maps Linux ACL tags and permissions to Samba `smb_acl_entry`, and fills uid/gid for named users/groups. Serialization maps Samba ACL entries back to little-endian tag/perm/id entries, writes version `0x0002`, and qsorts entries by tag then id. Get selects `system.posix_acl_access` or `system.posix_acl_default`, retries after ERANGE by querying actual size, parses the blob, and falls back to a three-entry mode-derived ACL on empty/missing xattr. Set serializes to alloca memory and writes via `SMB_VFS_FSETXATTR`; delete removes the default ACL xattr.

## State, Dependencies, Integration
No in-memory state persists between calls. Persistent state is the xattr content. Dependencies include Samba sys_acl structures, endian helpers, VFS fgetxattr/fsetxattr/fremovexattr, and POSIX ACL constants. It is integrated by GlusterFS and Ceph VFS modules.

## Risks And Test Signals
Risks include stack allocation sized by ACL entry count, strict version/size rejection, mode fallback masking missing default ACL semantics, and ordering changes from qsort. Tests should cover all ACL tags, invalid tags, malformed sizes, unknown version, ERANGE retry, ENOATTR fallback, access versus default names, large ACL counts, and byte-for-byte serialization ordering.
