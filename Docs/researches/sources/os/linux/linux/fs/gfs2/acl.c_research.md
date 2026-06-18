# File Research: sources/os/linux/linux/fs/gfs2/acl.c

Implements POSIX ACL get/set operations for GFS2 through system extended attributes.

Key entry points:
- `gfs2_get_acl()`
- `__gfs2_set_acl()`
- `gfs2_set_acl()`

Important control flow:
- `gfs2_acl_name()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`.
- ACL get returns `-ECHILD` under RCU lookup, acquires the inode glock in shared mode if needed, reads ACL xattr data, and converts it with `posix_acl_from_xattr()`.
- ACL set checks max ACL entries, gets quota accounting, acquires exclusive glock if needed, updates inode mode for access ACLs, stores/deletes xattr data, updates cached ACL, and marks inode dirty if mode changed.

Dependencies and integration:
- Uses GFS2 glocks, xattr helpers, quota accounting, transactions indirectly through xattr set, and Linux POSIX ACL helpers.

Risks and invariants:
- Max ACL entries are bounded by filesystem block size via `GFS2_ACL_MAX_ENTRIES`.
- `__gfs2_get_acl()` treats `gfs2_xattr_acl_get()` length <= 0 as an error pointer, so absence/error handling is delegated to xattr helper behavior.
