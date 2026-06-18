# File Research: sources/os/linux/linux-stable/fs/ext2/acl.c

## Summary
Implements ext2 POSIX ACL conversion, retrieval, update, and inheritance over ext2 extended attributes.

## Main Responsibilities
- Converts ACL xattr payloads between ext2 on-disk format and in-memory `struct posix_acl`.
- Reads access/default ACLs from xattrs.
- Writes access/default ACLs to xattrs and updates the VFS ACL cache.
- Initializes inherited ACLs for newly allocated inodes.

## Key APIs
- `ext2_get_acl()`.
- `ext2_set_acl()`.
- `ext2_init_acl()`.

## Important Behavior
On-disk ACLs start with `EXT2_ACL_VERSION`, then store short entries for owner/group/mask/other and full entries for named users/groups. UID/GID values are converted through `init_user_ns`.

`ext2_get_acl()` does not support RCU lookup and returns `-ECHILD` in RCU mode. `ext2_set_acl()` updates inode mode through `posix_acl_update_mode()` for access ACLs before storing the xattr. Default ACLs are accepted only for directories.

## Risks
ACL parsing is strict about entry sizes, tags, version, and trailing bytes. `ext2_set_acl()` uses `nop_mnt_idmap`, so idmapped mount semantics are not applied here.
