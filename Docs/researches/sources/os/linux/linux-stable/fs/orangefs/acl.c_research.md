# File Research: sources/os/linux/linux-stable/fs/orangefs/acl.c

## Scope

This file implements POSIX ACL get/set support for OrangeFS through extended attributes.

## APIs Covered

- `orangefs_get_acl()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`, retrieves the xattr, and converts it with `posix_acl_from_xattr()`.
- `__orangefs_set_acl()` converts an ACL to xattr form and writes/removes it with `orangefs_inode_setxattr()`.
- `orangefs_set_acl()` updates file mode when an access ACL can be represented in mode bits and then applies ACL storage.

## Control Flow And Behavior

- RCU ACL lookup is unsupported and returns `-ECHILD`.
- Missing ACL xattrs and server `-ENOSYS` are treated as no ACL.
- `NULL` ACL values translate to zero-length xattr writes, effectively remove operations.
- On successful set, the VFS ACL cache is updated with `set_cached_acl()`.
- Mode changes caused by ACL updates are propagated back through `__orangefs_setattr_mode()`.

## Risks And Invariants

- Allocates maximum xattr value length rather than probing, avoiding an extra network round trip.
- Uses `init_user_ns` for xattr ACL encoding/decoding.
- Invalid ACL type is rejected with `-EINVAL`.
