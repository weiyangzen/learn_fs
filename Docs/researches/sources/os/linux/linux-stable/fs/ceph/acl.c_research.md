# File Research: sources/os/linux/linux-stable/fs/ceph/acl.c

This file implements CephFS POSIX ACL get, set, pre-initialization, and inode cache initialization.

ACL cache handling:
- `ceph_set_cached_acl()` updates the VFS cached ACL only if the inode currently has `CEPH_CAP_XATTR_SHARED`; otherwise it forgets the cached ACL. This prevents caching ACLs without valid shared xattr capability from the MDS.

Get ACL:
- `ceph_get_acl()` rejects RCU mode with `-ECHILD`.
- It maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`.
- It first queries xattr size with `__ceph_getxattr()`, allocates a buffer if needed, then reads the xattr.
- It retries up to 10 times on `-ERANGE`, handling xattr size races.
- Positive data is decoded with `posix_acl_from_xattr()`.
- Missing or zero-length xattr yields `NULL`.
- Other failures are logged rate-limited and returned as `-EIO`.
- Successful non-error results are cached through `ceph_set_cached_acl()`.

Set ACL:
- `ceph_set_acl()` rejects snapshots with `-EROFS`.
- Access ACLs may update the inode mode through `posix_acl_update_mode()`.
- Default ACLs are allowed only on directories; setting a default ACL on non-directories returns `-EINVAL` unless removing it.
- ACLs are serialized with `posix_acl_to_xattr()`.
- If mode changes, it first calls `__ceph_setattr()` with new mode and ctime.
- Then it writes the ACL xattr with `__ceph_setxattr()`.
- If xattr write fails after a mode change, it attempts to restore the old mode and ctime.
- Successful updates refresh the cached ACL.

Create-time ACL initialization:
- `ceph_pre_init_acls()` calls `posix_acl_create()` for a new inode, simplifies equivalent access ACLs into mode bits, and builds a Ceph pagelist containing one or two xattr name/value pairs for access/default ACLs.
- It stores resulting ACL pointers and pagelist in `struct ceph_acl_sec_ctx`.
- It carefully releases ACLs, temporary xattr buffers, and pagelist on error.
- `ceph_init_inode_acls()` installs the prepared access/default ACLs into the new inode cache if the inode exists.

Important interactions:
- Uses Ceph MDS xattr and setattr helpers rather than local filesystem xattr ops.
- ACL caching is tied to Ceph capability state.
- Create-time ACLs are encoded into the request payload so the MDS can apply them atomically with inode creation.
