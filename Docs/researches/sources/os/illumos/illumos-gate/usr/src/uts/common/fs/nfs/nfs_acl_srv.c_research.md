# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_srv.c

## Purpose

This file implements the server-side handlers for the Solaris/illumos NFS ACL side protocol for NFSv2 and NFSv3 style clients. It translates ACL RPC requests into vnode operations and translates vnode errors and attributes back into NFS ACL protocol results.

## Main Responsibilities

- NFS ACL v2 server procedures:
  - `acl2_getacl()`
  - `acl2_setacl()`
  - `acl2_getattr()`
  - `acl2_access()`
  - `acl2_getxattrdir()`
- NFS ACL v3 server procedures:
  - `acl3_getacl()`
  - `acl3_setacl()`
  - `acl3_getxattrdir()`
- File-handle extraction helpers for RPC dispatch:
  - `acl2_getacl_getfh()`, `acl2_setacl_getfh()`, `acl2_getattr_getfh()`, `acl2_access_getfh()`, `acl2_getxattrdir_getfh()`
  - `acl3_getacl_getfh()`, `acl3_setacl_getfh()`, `acl3_getxattrdir_getfh()`
- Response cleanup helpers:
  - `acl2_getacl_free()`
  - `acl3_getacl_free()`

## Important Control Flow

`acl2_getacl()` and `acl3_getacl()`:

1. Convert the incoming file handle to a vnode with `nfs_fhtovp()` or `nfs3_fhtovp()`.
2. Initialize the response `vsecattr_t`.
3. Call `VOP_GETSECATTR()`.
4. If the filesystem returns `ENOSYS` and the export does not set `EX_NOACLFAB`, fabricate an ACL with `fs_fab_acl()`.
5. Fetch file attributes with `rfs4_delegated_getattr()`.
6. Convert attributes with `vattr_to_nattr()` for v2 or `vattr_to_post_op_attr()` for v3.
7. Free unrequested ACL/default-ACL arrays according to the request mask.

`acl2_setacl()` and `acl3_setacl()`:

1. Resolve the file handle.
2. Check read-only exports with `rdonly()`.
3. Take the vnode write lock.
4. Call `VOP_SETSECATTR()`.
5. Fetch post-operation attributes.
6. Return NFS status and attributes.

`acl2_access()`:

- Computes access bits by checking `VOP_ACCESS()` for read, lookup, modify, extend, delete, and execute.
- Suppresses write checks for regular files and directories on read-only exports.
- Denies read/write/execute bits on mandatory-lock files where appropriate.
- Returns full attributes after the access computation.

`acl2_getxattrdir()` and `acl3_getxattrdir()`:

- Resolve the base vnode.
- Use `LOOKUP_XATTR`, with `CREATE_XATTR_DIR` when requested.
- For non-create lookups, first checks `_PC_SATTR_EXISTS` and `_PC_XATTR_EXISTS` to avoid creating or looking up a missing hidden attribute directory unnecessarily.
- Calls `VOP_LOOKUP()` with an empty name and xattr flags.
- Builds a returned NFS file handle and attributes for the xattr directory.

## Error Handling

- v2 handlers return `NFSERR_STALE`, `NFSERR_ROFS`, `NFSERR_NOENT`, or `puterrno(error)` results.
- v3 handlers return `NFS3ERR_*` statuses via `puterrno3(error)`.
- v3 GETACL and SETACL translate `T_WOULDBLOCK` into `NFS3ERR_JUKEBOX`.
- On failed GETACL after ACL allocation, the code frees allocated ACL arrays before returning.
- v3 failure results include weak/post-op attributes when available.

## Dependencies

- Vnode operations:
  - `VOP_GETSECATTR`
  - `VOP_SETSECATTR`
  - `VOP_GETATTR`
  - `VOP_ACCESS`
  - `VOP_LOOKUP`
  - `VOP_PATHCONF`
  - `VOP_RWLOCK`
  - `VOP_RWUNLOCK`
- NFS helpers:
  - `nfs_fhtovp`
  - `nfs3_fhtovp`
  - `makefh`
  - `makefh3`
  - `vattr_to_nattr`
  - `vattr_to_post_op_attr`
  - `rfs4_delegated_getattr`
- ACL/filesystem helpers:
  - `fs_fab_acl`
  - `rdonly`
- Kernel allocation:
  - `kmem_free`

## State and Memory Ownership

This file does not own global state. It allocates no persistent objects but must free ACL arrays returned by `VOP_GETSECATTR()` or `fs_fab_acl()` when those arrays are not returned to the RPC layer or when response cleanup is called. The response cleanup helpers free only successful GETACL responses.

## Risks and Edge Cases

- ACL fabrication exists specifically for filesystems like ZFS that support ACE-style ACLs but not `aclent_t`; export option `EX_NOACLFAB` disables this compatibility behavior.
- `acl2_getxattrdir()` and `acl3_getxattrdir()` guard against old filesystems returning the same vnode for empty-name xattr lookup.
- `acl3_setacl()` uses shared cleanup labels; the vnode is unlocked and released through `out1` when held.
- Extended attribute existence probes are best-effort; errors from `_PC_SATTR_EXISTS` and `_PC_XATTR_EXISTS` do not by themselves stop lookup unless both probes prove absence.

## Testing Notes

Relevant coverage should include:

- GETACL with native ACL support.
- GETACL with `ENOSYS` and fabricated ACLs.
- GETACL with masks excluding ACL/default ACL arrays.
- SETACL on writable and read-only exports.
- ACCESS on mandatory-lock files and read-only exports.
- GETXATTRDIR create and non-create paths for v2 and v3.
- v3 `T_WOULDBLOCK` to `NFS3ERR_JUKEBOX` translation.
