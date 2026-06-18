# File Research: sources/os/linux/linux-stable/fs/f2fs/acl.c

## Purpose
Implements F2FS POSIX ACL serialization, deserialization, get/set operations, permission-mode updates, ACL inheritance, and new-inode ACL initialization.

## Main Components
- `f2fs_acl_size()` and `f2fs_acl_count()` encode/decode the compact on-disk ACL format where the first four standard entries omit an ID field.
- `f2fs_acl_from_disk()` validates version and entry layout, converts little-endian tags/perms/ids into `struct posix_acl`, and rejects malformed sizes or tags.
- `f2fs_acl_to_disk()` serializes `struct posix_acl` back to F2FS xattr format.
- `__f2fs_get_acl()` reads ACL xattrs with indexes `F2FS_XATTR_INDEX_POSIX_ACL_ACCESS` or `DEFAULT`.
- `f2fs_set_acl()` rejects checkpoint-error filesystems with `-EIO`, then writes ACL xattrs through `f2fs_setxattr()`.
- Access ACL updates call `posix_acl_equiv_mode()` and update inode mode, including setgid clearing when the caller lacks group/capability authority.
- ACL create helpers clone and mask parent default ACLs for new inodes, applying `current_umask()` when no default ACL exists.
- `f2fs_init_acl()` writes inherited default/access ACLs during inode creation and marks inode metadata dirty.

## Dependencies
Depends on F2FS xattr helpers, inode dirtying, POSIX ACL core helpers, idmapped mount checks, and F2FS checkpoint error state.

## Research Notes
Malformed on-disk ACL data returns `-EINVAL`. The create path mirrors generic POSIX ACL logic but is local so it can pass F2FS folios into xattr operations.
