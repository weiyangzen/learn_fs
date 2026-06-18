# File Research: sources/os/linux/linux/fs/9p/acl.c

## Summary
Implements POSIX ACL support for the 9p filesystem using server xattrs and inode ACL caching.

## Main Responsibilities
- Reads ACL xattrs through 9p fids and converts them to `struct posix_acl`.
- Caches access/default ACLs on inode instantiation.
- Provides inode and dentry ACL get/set operations.
- Updates remote ACL xattrs on chmod and create.
- Applies inherited default ACLs to create modes.

## Key APIs
- `v9fs_get_acl()`.
- `v9fs_iop_get_inode_acl()`, `v9fs_iop_get_acl()`, `v9fs_iop_set_acl()`.
- `v9fs_acl_chmod()`.
- `v9fs_set_create_acl()`.
- `v9fs_acl_mode()`.
- `v9fs_put_acl()`.

## Important Behavior
When access mode is not `V9FS_ACCESS_CLIENT` or ACL mode is not `V9FS_POSIX_ACL`, inode ACL caches are set to NULL and client-side ACL enforcement is bypassed.

For `access=client`, get operations use cached ACLs populated during inode creation. For other access modes, dentry get/set paths use server xattrs directly.

Setting an access ACL validates it, converts it to xattr format, may update inode mode via `posix_acl_update_mode()`, rejects symlinks, requires ownership/capability, and updates the cached ACL on success. Default ACLs are valid only on directories.

`v9fs_acl_mode()` applies a parent default ACL during create; without a default ACL it applies the current umask.

## State and Lifetime
ACL objects are reference-counted with `posix_acl_release()`. Serialized xattr buffers are dynamically allocated and freed after server calls.

## Risks
ACL behavior changes substantially based on mount/session flags. `v9fs_set_create_acl()` ignores return values from the two remote ACL writes, so create-time cache state can be updated even if server xattr persistence fails.
