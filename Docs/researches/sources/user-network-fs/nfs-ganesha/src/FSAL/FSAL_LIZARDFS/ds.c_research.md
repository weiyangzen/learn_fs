# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/ds.c

Purpose: Implements LizardFS pNFS data-server handle operations: converting layout wire handles to DS handles, cached file opening, DS read/write/commit, and DS handle cleanup.

Important APIs and types: `struct lzfs_fsal_ds_wire` carries a 32-bit inode over the wire. `struct lzfs_fsal_ds_handle` stores the inode and optional `liz_fileinfo_cache` entry. Registered ops are `make_ds_handle`, `dsh_release`, `dsh_read`, `dsh_write`, `dsh_commit`, and `dsh_read_plus`.

Control flow: `lzfs_fsal_make_ds_handle()` validates descriptor size and inode, handles endian conversion, allocates a DS handle, and returns it. DS read/write/commit call `lzfs_int_openfile()`; that function reuses an existing cache entry, pops expired entries, acquires a cache entry by inode, opens the file with `O_RDWR` using null credentials if needed, and attaches the fileinfo. Read and write call `liz_cred_read()`/`liz_cred_write()`. Commit and stable writes flush through `liz_cred_flush()`. Release returns the cache entry and opportunistically clears expired cache entries.

State and persistence: DS state is the per-export `fileinfo_cache` plus per-DS-handle cache entry references. Persistent file data is in LizardFS. `writeverf` is zeroed on commit; write operation does not fill verifier in the shown path.

Dependencies and integration: Depends on `op_ctx->ctx_pnfs_ds->mds_fsal_export`, `pnfs_utils`, LizardFS wrappers, and fileinfo cache APIs. Export creation in `main.c` creates the fileinfo cache when pNFS DS support is enabled.

Risks: `lzfs_fsal_ds_handle_commit()` returns `NFS4_OK` if opening the file fails, which may mask real commit failures. DS open always uses `O_RDWR` and null credentials, so authorization model depends on pNFS/MDS layout validation rather than DS operation credentials. Cache eviction and release must match LizardFS fileinfo lifetimes. `read_plus` is unimplemented. Stable write returns `UNSTABLE4` on flush failure but still returns `NFS4_OK`.

Test signals: pNFS DS read/write/commit with cached and expired fileinfo entries, invalid/big-endian DS handles, stable write flush failures, cache saturation, concurrent DS handles for one inode, and client behavior when READ_PLUS is requested.
