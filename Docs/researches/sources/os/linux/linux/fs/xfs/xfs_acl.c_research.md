# File Research: sources/os/linux/linux/fs/xfs/xfs_acl.c

Implements XFS POSIX ACL conversion, get/set operations, mode synchronization, and ACL cache invalidation.

Key elements:
- `xfs_acl_from_disk` validates the on-disk ACL header/count/size, allocates a VFS `posix_acl`, converts big-endian XFS ACL entries to in-core entries, and maps ids through `init_user_ns`.
- `xfs_acl_to_disk` converts a VFS ACL to the XFS on-disk xattr format.
- `xfs_get_acl` selects `SGI_ACL_FILE` or `SGI_ACL_DEFAULT`, fetches the root namespace xattr, and converts it to a `posix_acl`.
- `__xfs_set_acl` upserts or removes the root namespace ACL xattr and updates the cached ACL on success.
- `xfs_acl_set_mode` logs inode mode changes in a transaction after ACL updates.
- `xfs_set_acl` validates ACL size, uses `posix_acl_update_mode` for access ACLs, applies the xattr update first, and then updates mode.
- `xfs_forget_acl` invalidates cached access/default ACLs when raw xattr paths modify ACL names.

Dependencies:
- Uses xattr/attr machinery: `xfs_attr_get`, `xfs_attr_change`, `XFS_ATTR_ROOT`.
- Uses VFS ACL helpers: `posix_acl_alloc`, `posix_acl_update_mode`, `set_cached_acl`, `forget_cached_acl`.

Research notes:
- Default ACLs are allowed only on directories; removing a nonexistent default ACL on a non-directory returns success.
- ACL xattr update precedes mode update to avoid changing mode if the xattr operation fails with `ENOSPC`.
- Malformed on-disk ACLs return `-EFSCORRUPTED` after logging corruption.
