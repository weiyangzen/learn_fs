# File Research: sources/os/linux/linux-stable/fs/ceph/xattr.c

## Purpose
Implements CephFS extended attribute get/list/set handling, cached xattr blob parsing/rebuilding, virtual `ceph.*` xattrs, security-label initialization, and VFS xattr handler registration.

## Main Interfaces
- Generic xattrs: `__ceph_getxattr()`, `__ceph_setxattr()`, `ceph_listxattr()`.
- Blob/cache helpers: `__ceph_build_xattrs_blob()`, `__ceph_destroy_xattrs()`.
- Virtual xattr dispatch: internal `ceph_match_vxattr()` and vxattr callback tables.
- Security helpers: `ceph_security_xattr_wanted()`, `ceph_security_xattr_deadlock()`, `ceph_security_init_secctx()`.
- Context cleanup: `ceph_release_acl_sec_ctx()`.
- VFS handler table: `ceph_xattr_handlers`.

## Control Flow
Regular xattrs are cached as an MDS-provided encoded blob until first use. `__build_xattrs()` decodes that blob into an rb-tree of `ceph_inode_xattr` entries under `i_ceph_lock`, allocating outside the spinlock and retrying if the xattr version changes. `__ceph_getxattr()` fetches `CEPH_CAP_XATTR_SHARED` from the MDS when the cache is missing or unauthorized, then looks up the rb-tree entry. `ceph_listxattr()` similarly ensures xattr caps and copies null-terminated names.

`__ceph_setxattr()` uses a fast local update when the inode has exclusive xattr caps, the xattr blob is known, and the rebuilt blob would not exceed the MDS max xattr size. It preallocates name/value/index storage, cap-flush state, and a buffer for the rebuilt blob, then marks xattr caps dirty. Otherwise it sends synchronous `SETXATTR` or `RMXATTR` requests to the MDS.

Virtual xattrs expose layout, directory stats, recursive stats, quota, snapshot birth time, caps, auth MDS, cluster FSID, client ID, and fscrypt auth. Some are readonly or hidden; some force getattr masks such as `CEPH_STAT_RSTAT` or `CEPH_CAP_FILE_SHARED`.

## State And Synchronization
`ci->i_xattrs` contains the blob, preallocated blob, rb-tree index, dirty flag, counts, sizes, and version numbers, protected by `i_ceph_lock`. Snap interactions may require taking `mdsc->snap_rwsem` before dirtying xattrs so cap-snap boundaries are respected. OSD map pool-name lookups use `osdc->lock`.

## Integration Points
The file integrates with MDS getattr/setxattr requests, caps dirtying/flushing, security modules, POSIX ACL/security creation context pagelists, fscrypt auth xattrs, quota snaprealm validation, and VFS xattr handlers.

## Risks And Review Focus
- Local xattr mutation must recompute blob size after rebuilding because races can replace the blob while the spinlock is dropped.
- Security xattr access during trace filling returns `-EBUSY` to avoid deadlock.
- Virtual xattr existence/read-only flags must match MDS semantics, especially quota and fscrypt fields.
- Synchronous fallback is required when caps or size limits do not permit local mutation.
