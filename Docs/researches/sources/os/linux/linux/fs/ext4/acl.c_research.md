# File Research: sources/os/linux/linux/fs/ext4/acl.c

## Purpose
Implements ext4 POSIX ACL conversion, retrieval, setting, and new-inode ACL initialization.

## Main Responsibilities
- `ext4_acl_from_disk()` validates and converts ext4 xattr ACL bytes into `struct posix_acl`.
- `ext4_acl_to_disk()` serializes in-memory ACLs to ext4 ACL xattr format.
- `ext4_get_acl()` fetches access/default ACL xattrs and converts them.
- `ext4_set_acl()` starts a journal transaction, updates mode for access ACLs via `posix_acl_update_mode()`, writes the xattr, marks inode dirty when needed, and retries allocation on ENOSPC.
- `ext4_init_acl()` derives ACLs from the parent directory during inode creation and writes default/access ACL xattrs with `XATTR_CREATE`.

## Integration Points
Uses ext4 xattr APIs, JBD2 handles, quota initialization, inode dirtying, POSIX ACL core helpers, and idmapped mount information for mode updates.

## Risks and Edge Cases
Default ACLs are valid only on directories. ACL xattr sizing affects journal credit calculation. Disk parsing rejects malformed entry counts, unknown tags, truncated entries, and trailing bytes.
