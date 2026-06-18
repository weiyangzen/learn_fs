# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/export.c

## Purpose

`export.c` implements Ceph FSAL export-level operations: export teardown, path lookup, NFS filehandle digest conversion, host-handle lookup, dynamic filesystem information, ACL capability reporting, unexport preparation, and export operation-vector registration. The complete 534-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `release`, `lookup_path`, `wire_to_host`, `host_to_key`, `create_handle`, `get_fs_dynamic_info`, `fs_acl_support`, `ceph_prepare_unexport`, `get_fsal_obj_hdl`, `fs_supported_attrs`, and `export_ops_init`. It works primarily with `struct ceph_export`, `struct ceph_mount`, `struct ceph_handle`, `struct ceph_host_handle`, `struct ceph_handle_key`, `struct ceph_statx`, `struct gsh_buffdesc`, and Ganesha `export_ops`.

## Control Flow

Export release deconstructs the root handle, detaches the export, removes it from the shared `ceph_mount` export list, decrements the mount refcount under `cmount_lock`, and shuts down/removes the shared libcephfs mount when the last export releases it. Path lookup normalizes `host:/path` forms, verifies the requested path starts under `CTX_FULLPATH(op_ctx)`, strips the shared mount prefix, special-cases the export root, then calls `fsal_ceph_ll_walk` and `construct_handle`. Filehandle decode converts little-endian wire fields to host values; `host_to_key` adds the current export id back into the cache key. `create_handle` validates the host handle length, reconstructs a `vinodeno_t`, finds the Ceph inode, fetches enough statx data, and constructs the FSAL handle.

## State and Persistence Behavior

This file manages no disk persistence directly, but it is responsible for shared mount lifetime and inode-cache identity. `release` is the main persistence-adjacent path because `ceph_shutdown` ends the libcephfs client session, and `ceph_prepare_unexport` calls `ceph_sync_fs` before unexport. Filehandle state is stable across NFS clients through the packed inode, snap, fscid tuple plus Ganesha's export id handling.

## Dependencies and Integration Points

Dependencies include libcephfs low-level calls through `statx_compat.h`, Ganesha FSAL export APIs, `cmount_lock`/AVL mount registry from `internal.c`, op-context export path data, NFS core shutdown/grace state, LTTng tracepoints, and optional POSIX ACL support. It integrates with `main.c` export creation, `internal.c` handle construction, and `handle.c` object operations.

## Risks and Edge Cases

Path prefix validation depends on string layout after `cmount_path` trimming; mismatches can return server fault rather than a clearer stale/cross-export error. `host_to_key` depends on `op_ctx->ctx_export`, so callers must have a valid export context. Legacy little-endian filehandle compatibility must not regress. `release` assumes `op_ctx->fsal_export` matches the handle being deconstructed through `deconstruct_handle`. Shutdown behavior differs when `USE_FSAL_CEPH_ABORT_CONN` is compiled.

## Test Signals

Useful tests include exporting both `/` and subdirectories with and without `cmount_path`, NFSv3/NFSv4 filehandle round trips across restart, stale inode lookup, multiple exports sharing a `ceph_mount` with different refcounts, unexport during admin shutdown/grace, statfs reporting with subvolume quotas, ACL-disabled exports masking `ATTR_ACL`, and LTTng/debug trace smoke checks for handle creation.
