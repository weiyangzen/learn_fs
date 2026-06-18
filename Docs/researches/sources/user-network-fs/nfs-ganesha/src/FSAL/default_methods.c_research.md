## sources/user-network-fs/nfs-ganesha/src/FSAL/default_methods.c

### Purpose
`default_methods.c` defines the process-wide default method vectors for FSAL modules, exports, object handles, pNFS data servers, and pNFS data-server handles. These defaults provide ABI-compatible fallback behavior when older or simpler FSALs do not implement newer hooks: unsupported operations generally return `ERR_FSAL_NOTSUPP`, pNFS operations return NFSv4 errors, and capability accessors delegate to shared FSAL static configuration.

### Important APIs, Types, And Functions
The exported globals are `def_fsal_ops`, `def_export_ops`, `def_handle_ops`, and `def_pnfs_ds_ops`, declared privately in `fsal_private.h` and copied during FSAL registration. Module-level defaults include `unload_fsal`, `init_config`, `update_config`, `create_export`, `update_export`, `create_fsal_pnfs_ds`, `fsal_pnfs_ds_ops`, `fsal_extract_stats`, `fsal_reset_stats`, and NFS service registration hooks. Export-level defaults include capability getters such as `fs_supports`, `fs_maxfilesize`, `fs_acl_support`, `fs_supported_attrs`, quota stubs, pNFS layout capability stubs, `global_verifier`, and `alloc_state`. Object-level defaults include lookup/create/link/rename/unlink/xattr/layout/open/read/write/lock/setattr/close hooks, `handle_cmp`, `handle_to_key`, `check_verifier`, `compute_readdir_cookie`, and `is_referral`. pNFS data server defaults include `pds_release`, `pds_permissions`, `pds_handle`, `ds_read`, `ds_read_plus`, `ds_write`, and `ds_commit`.

### Control Flow
Registration code copies these vectors, after which each FSAL overrides the methods it supports. Callers route through module, export, or object operation tables. Unsupported defaults log through FSAL or PNFS components and return stable error codes. `unload_fsal` locks `fsal_lock`, refuses unload if references or exports remain, rejects statically linked modules, removes the FSAL from `fsal_list`, destroys the module rwlock, and `dlclose`s the shared object. `update_export` only validates stacking consistency between the original export and updated super-FSAL. `check_verifier` obtains atime and mtime through `getattrs` and compares them with the NFS exclusive-create verifier.

### State And Persistence
The file owns no persistent storage but manipulates FSAL process state through copied operation vectors. `unload_fsal` changes the global FSAL list and shared-object lifetime. `global_verifier` reads the global `NFS4_write_verifier`. pNFS DS defaults allocate and release `fsal_pnfs_ds` and `fsal_ds_handle` objects. `pds_permissions` mutates `op_ctx->export_perms` to root operation defaults for DS requests.

### Dependencies And Integration Points
It depends on `fsal.h`, `fsal_private.h`, `FSAL/fsal_config.h`, localfs and commonlib helpers, pNFS utilities, NFS core state, and credential context. `fsal_manager.c` consumes `def_fsal_ops` during `register_fsal`; FSAL implementations typically copy or override `def_export_ops` and `def_handle_ops` for export/object initialization. `fsal_helper.c` depends on object methods defaulted here when performing higher-level policy wrappers.

### Risks
The `unload_fsal` error path calls `PTHREAD_RWLOCK_unlock(&fsal_hdl->fsm_lock)` even though this function does not acquire that rwlock in the visible code, which is a shutdown risk if exercised. Silent no-op reference methods require an upper layer such as MDCACHE to override them; direct use without overrides can leak or mishandle handle lifetimes. Defaults that return success for `lookup_junction`, `check_quota`, `handle_merge`, or `io_advise` are deliberately permissive and can hide missing FSAL-specific semantics. `pds_handle` allocates a generic DS handle while logging unimplemented behavior, so incomplete pNFS DS support may progress farther than expected before failing reads/writes.

### Test Signals
Tests should verify that newly registered FSALs receive all default vector entries, unsupported object/export operations map to expected FSAL or NFSv4 errors, capability getters reflect `fsal_staticfsinfo_t`, exclusive create verifier comparison uses atime/mtime correctly, unload refuses busy or static FSALs, and partial pNFS DS defaults release all allocations on shutdown.
