# File Research: sources/os/linux/linux/fs/orangefs/acl.c

Implements POSIX ACL get/set support for OrangeFS by storing ACLs in OrangeFS extended attributes.

Key behavior:
- `orangefs_get_acl()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`, fetches the xattr via `orangefs_inode_getxattr()`, and converts it with `posix_acl_from_xattr()`.
- RCU ACL lookup returns `-ECHILD`; OrangeFS performs blocking xattr RPCs.
- `__orangefs_set_acl()` converts ACLs with `posix_acl_to_xattr()` and writes/removes the backing xattr through `orangefs_inode_setxattr()`, then updates the VFS ACL cache.
- `orangefs_set_acl()` uses `posix_acl_update_mode()` for access ACLs, writes the ACL, and propagates resulting mode changes with `__orangefs_setattr_mode()`.

Important interactions:
- Depends on xattr implementation and inode setattr path.
- Treats missing ACL xattrs and unsupported ACL operations as no ACL (`NULL`) for get.
