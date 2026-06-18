# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/statx_compat.h

## Purpose

`statx_compat.h` defines the Ceph FSAL statx compatibility interface. With newer libcephfs it provides inline wrappers that create/destroy `UserPerm` and call statx-capable APIs; without it, it defines a local `struct ceph_statx`, statx/setattr masks, fallback prototypes, and inline wrappers for operations that do not need stat conversion. The complete 532-line file was read for this report.

## Important APIs, Types, and Functions

Important definitions are `CEPH_STATX_HANDLE_MASK`, `CEPH_STATX_ATTR_MASK`, `user_cred2ceph`, wrappers named `fsal_ceph_ll_*`, fallback `struct ceph_statx`, `CEPH_STATX_*` masks, `CEPH_SETATTR_*` masks from libcephfs context, and `AT_NO_ATTR_SYNC` fallback.

## Control Flow

In statx builds, each inline wrapper converts `struct user_cred` into a libcephfs `UserPerm`, calls the corresponding `ceph_ll_*` operation with full or handle-only stat masks, destroys the permission object, and returns the libcephfs status. In fallback builds, stat-returning operations are implemented in `statx_compat.c`, while simple operations such as readlink/open/opendir/link/unlink/rename/rmdir/xattr call older uid/gid libcephfs APIs directly.

## State and Persistence Behavior

The header stores no state, but it centralizes credential translation and determines whether auxiliary groups reach libcephfs. Persistent effects are delegated to callers through create, setattr, xattr, namespace, and I/O operations. The chosen stat mask controls which attributes upper layers consider valid.

## Dependencies and Integration Points

Dependencies include `fsal_types.h`, libcephfs types (`UserPerm`, `Inode`, `Fh`, `ceph_statx`), POSIX mode/dev/time types, and build-system feature detection. It is included by Ceph export, handle, internal, main, and fallback compatibility code.

## Risks and Edge Cases

Every wrapper allocates a `UserPerm`; allocation failure returns `-ENOMEM` and must be mapped by callers. Statx and fallback builds have subtly different permission semantics, attribute availability, and sync behavior. Wrapper signatures must stay synchronized with call sites; pNFS code in this tree appears out of sync for some `fsal_ceph_ll_getattr/setattr` uses. Since most wrappers are inline, compile coverage is the primary guard.

## Test Signals

Useful signals are dual builds with and without `USE_FSAL_CEPH_STATX`, full auxiliary-group permission tests, allocation-failure injection for `ceph_userperm_new`, stat mask coverage for handle-only and full-attribute lookups, xattr namespace operations, and compile tests for all feature combinations that include pNFS, ACL, mknod, and sync-inode.
