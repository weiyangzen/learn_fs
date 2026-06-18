# sources/user-network-fs/samba/source3/modules/posixacl_xattr.h

## Purpose
Declares POSIX ACL over xattr helper APIs.

## APIs, Types, And Control Flow
Exports `posixacl_xattr_acl_get_fd()`, `posixacl_xattr_acl_set_fd()`, and `posixacl_xattr_acl_delete_def_fd()`. These mirror Samba sys_acl VFS hooks for reading, writing, and deleting default ACLs on an open file.

## State, Dependencies, Integration
The header has no state. It relies on Samba VFS, file, ACL, and talloc types from including code. GlusterFS and Ceph VFS modules use it to route sys_acl hooks through xattr persistence.

## Risks And Test Signals
Callers must pass a valid ACL type and open file structure; invalid types map to `EINVAL` in the implementation. Compile tests should confirm hook signatures remain compatible with `struct vfs_fn_pointers`.
