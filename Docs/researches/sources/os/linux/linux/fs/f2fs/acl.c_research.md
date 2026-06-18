# File Research: sources/os/linux/linux/fs/f2fs/acl.c

## Purpose
Implements F2FS POSIX ACL conversion, retrieval, setting, and inode-initialization behavior using F2FS xattrs.

## Main Responsibilities
- Converts between F2FS compact on-disk ACL encoding and VFS `struct posix_acl`.
- Retrieves access/default ACLs through `f2fs_getxattr()`.
- Stores ACLs through `f2fs_setxattr()`.
- Updates inode mode bits when access ACLs are equivalent or when permissions must be masked.
- Initializes new inode ACLs from parent default ACLs.

## Key Functions
- `f2fs_acl_size()` and `f2fs_acl_count()` calculate compact ACL storage sizes and entry counts.
- `f2fs_acl_from_disk()` validates version, decodes short/full ACL entries, maps ids through `init_user_ns`, and returns a VFS ACL.
- `f2fs_acl_to_disk()` encodes VFS ACLs into F2FS disk format.
- `f2fs_get_acl()` rejects RCU lookup with `-ECHILD` and delegates to xattr-backed lookup.
- `f2fs_set_acl()` rejects checkpoint-error filesystems with `-EIO`, then calls `__f2fs_set_acl()`.
- `f2fs_init_acl()` derives default/access ACLs for newly created inodes and marks inode metadata dirty.

## Edge Cases
- Non-directory default ACL set returns `-EACCES` when an ACL is supplied.
- Symlinks and non-POSIXACL parents skip inherited ACL creation.
- If inherited ACL is equivalent to mode bits, the access ACL is dropped and only mode is updated.
- Invalid on-disk ACL tags, sizes, or version return `-EINVAL`.
