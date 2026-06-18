# File Research: sources/os/linux/linux/fs/afs/xattr.c

## Scope

This file exposes AFS metadata and ACL operations through Linux extended attributes, replacing pioctl-style metadata access for ACLs, cell name, FID, volume name, and YFS opaque ACL fields.

## Public And Internal APIs Covered

- Xattr handlers for `afs.acl`, `afs.cell`, `afs.fid`, `afs.volume`, and prefix `afs.yfs.`.
- ACL operation helpers for fetch/store AFS3 ACL and fetch/store YFS opaque ACL.
- Exported handler table: `afs_xattr_handlers`.

## Control Flow And Behavior

- `afs_xattr_get_acl()` issues an AFS FetchACL operation, returns the ACL size for size probes, copies data when the buffer is large enough, and returns `-ERANGE` otherwise.
- `afs_xattr_set_acl()` rejects `XATTR_CREATE`, copies the supplied ACL into the operation, and issues StoreACL.
- YFS gets support names `acl`, `acl_inherited`, `acl_num_cleaned`, and `vol_acl`. It requests only needed ACL payloads and maps unsupported YFS RPCs from `-ENOTSUPP` to `-ENODATA`.
- YFS set only accepts `afs.yfs.acl` and uses `StoreOpaqueACL2`.
- Metadata xattrs return the cell name, formatted FID (`vid:vnode:unique` with 96-bit vnode support), and volume name.
- Successful ACL operations commit vnode status from the returned status callback.

## State And Data Structures

- `struct afs_acl` holds variable-sized ACL data copied into/out of operations.
- `struct yfs_acl` holds YFS opaque ACL result fields, inherited flag, cleaned count, and optional volume ACL.

## Dependencies

- AFS/YFS filesystem RPC implementations, AFS operation framework, Linux xattr handler API, vnode status commit, and YFS ACL free helper.

## Risks And Invariants

- Xattr size-probe semantics return required length when `size == 0`.
- Store operations allocate/copy ACL data before RPC dispatch; operation `.put` frees it.
- YFS ACL handler must reject unsupported subnames to avoid ambiguous metadata writes.
