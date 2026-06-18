# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/handle.c

## Purpose

`handle.c` is the main Ceph FSAL object-operation implementation. It maps Ganesha `fsal_obj_ops` to libcephfs operations for lookup, readdir, create, mkdir, mknod, symlink, readlink, getattr, link, rename, unlink, open/create, read/write, commit, locks, delegations, setattr, close, filehandle encoding, fallocate, and NFSv4 xattrs. The complete 3469-line file was read for this report.

## Important APIs, Types, and Functions

Important entry points include `ceph_fsal_release`, `ceph_fsal_lookup`, `ceph_fsal_readdir`, `ceph_fsal_mkdir`, `ceph_fsal_mknode`, `ceph_fsal_symlink`, `ceph_fsal_readlink`, `ceph_fsal_getattrs`, `ceph_fsal_link`, `ceph_fsal_rename`, `ceph_fsal_unlink`, `ceph_open2_by_handle`, `ceph_fsal_open2`, `ceph_fsal_read2`, `ceph_fsal_write2`, `ceph_fsal_commit2`, `ceph_fsal_lock_op2`, `ceph_deleg_cb`, `ceph_fsal_lease_op2`, `ceph_fsal_setattr2`, `ceph_fsal_close2`, `ceph_fsal_handle_to_wire`, `ceph_fsal_fallocate`, xattr helpers, and `handle_ops_init`. Core private state is `struct ceph_handle`, `struct ceph_fd`, `struct ceph_state_fd`, `struct ceph_fsal_cb_info`, and `struct fsal_share`.

## Control Flow

Object creation and lookup paths call statx compatibility wrappers, construct Ceph handles, and optionally post-apply attributes through `setattr2`. `open2` has separate open-by-handle and open-by-name flows: non-create by-name performs lookup first, create-by-name calls `fsal_ceph_ll_create`, handles exclusive/unchecked semantics, constructs the handle, installs a global or state fd, and sets remaining attributes only when it knows it created the file. Read/write paths call `fsal_start_io`, perform synchronous `ceph_ll_read`/`ceph_ll_write` loops or optional nonblocking libcephfs I/O, complete I/O through FSAL fd helpers, update temporary share counters, and invoke the caller callback. Metadata operations translate FSAL masks to Ceph set/get masks and security-label xattrs. `handle_ops_init` installs all implemented operations over defaults.

## State and Persistence Behavior

The file owns per-object and per-state fd lifecycle through `fsal_fd`, fd LRU insertion/removal, `close_fsal_fd`, and libcephfs `Fh *` handles. Share-deny state is kept in `struct fsal_share` on the object and updated under `obj_lock`. Stateless I/O and truncate paths temporarily acquire share counters and release them after completion. Persistent effects are CephFS namespace changes, file data writes, fsync/commit, xattrs, security labels, POSIX ACL xattrs, delegation/lock state in libcephfs/MDS, and optional fallocate/punch-hole changes.

## Dependencies and Integration Points

Dependencies include libcephfs low-level APIs, `statx_compat.h`, Ganesha fd/share/state helpers, POSIX ACL conversion, security label export options, `nfs_core` shutdown state, Linux fallocate constants, optional nonblocking and zerocopy Ceph I/O, optional lock and delegation libcephfs APIs, and LTTng tracepoints. The file depends on `internal.c` for handle construction and attribute conversion and on `main.c` for module feature flags such as `CephFSM.async` and `CephFSM.zerocopy`.

## Risks and Edge Cases

The file is heavily compile-option dependent, so matrix builds are important. Create cleanup admits a rare unchecked-create race that can leave a partially created file after later errors. Some metadata updates temporarily use root credentials, especially security labels after restrictive creates. Async callbacks construct a lightweight op context and rely on the original request lifetime retaining export references until callback completion. `ceph_fsal_reopen2` temporarily overwrites `op_ctx->creds`. Lock range validation guards signed `flock.l_len` overflow, but conflicting-lock translation uses POSIX structures directly. Xattr names are forced into `user.*`, so namespace assumptions are protocol-visible.

## Test Signals

Strong signals include create/open verifier behavior, unchecked create fallback, share-deny conflicts, fd LRU counts after open/reopen/close, stateless and stateful read/write, async and zerocopy read/write callbacks, stable write and commit/fsync behavior, truncate with and without state, rename over non-empty directory mapping to `EEXIST`, security label get/set with permission edge cases, POSIX ACL round trips, lock test/set/unlock, delegation recall callback behavior, fallocate and punch-hole if compiled, and NFSv4 xattr list/get/set/remove errors for `ERANGE` and missing xattrs.
