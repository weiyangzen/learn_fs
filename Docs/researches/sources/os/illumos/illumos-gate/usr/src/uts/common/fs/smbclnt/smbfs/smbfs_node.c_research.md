# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_node.c

## Scope

This file implements small SMBFS node helpers for pseudo-inode hashing, name allocation, lookup/create glue, and attribute cache invalidation.

## APIs And Behavior

- `smbfs_hash()` is an FNV-style 32-bit hash helper.
- `smbfs_gethash()` computes a hash of a full remote path.
- `smbfs_getino()` computes a child pseudo-inode number from the parent inode hash, optional separator, and child name.
- `smbfs_name_alloc()` allocates and null-terminates a fixed-length name.
- `smbfs_name_free()` frees names allocated by `smbfs_name_alloc()`.
- `smbfs_nget()` validates a lookup name, builds/finds/creates a node through `smbfs_node_findcreate()`, propagates `N_XATTR` from parent to child, and returns the vnode.
- `smbfs_attr_touchdir()` updates a directory’s local modification time and invalidates its attribute cache.
- `smbfs_attrcache_remove()` expires a node’s attribute cache.
- `smbfs_attrcache_rm_locked()` expires a node’s attribute cache while caller holds `r_statelock`.

## Dependencies

- Relies on node cache functionality declared elsewhere, mount/node structures, and SMBFS subr helpers.
- Uses `SMBFS_DNP_SEP()` for remote path separator semantics.

## Risks And Invariants

- Node identity is the full server-form remote path relative to the share root.
- Empty, `.` and `..` names are rejected before node creation.
- Pseudo-inode numbers are hashes and may collide; they are not server-provided stable IDs.
