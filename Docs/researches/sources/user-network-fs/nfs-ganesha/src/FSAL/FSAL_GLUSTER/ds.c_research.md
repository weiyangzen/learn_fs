# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/ds.c

## Purpose

`ds.c` implements Gluster FSAL pNFS data-server operations. It creates DS handles from client wire handles, supports direct anonymous GFAPI read/write by object handle, commits stable writes, releases DS handles, and registers DS operation vectors. The complete 298-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `dsh_release`, `ds_read`, `ds_write`, `ds_commit`, `make_ds_handle`, and `pnfs_ds_ops_init`. Important types include `struct glfs_ds_handle`, `struct glfs_ds_wire`, `struct glusterfs_export`, `struct fsal_pnfs_ds`, `struct fsal_ds_handle`, `stateid4`, and NFSv4 stability/verifier types.

## Control Flow

`make_ds_handle` validates the wire handle size, copies the GFAPI object handle, creates a `glfs_object` with `glfs_h_create_from_handle`, and returns a DS handle. `ds_read` uses `glfs_h_anonymous_read` against the MDS export's GFAPI context and sets EOF on short or zero read. `ds_write` zeroes the verifier, writes with `glfs_h_anonymous_write`, records stability, and invalidates the MDS-side cache via `up_process_event_object`. `ds_commit` opens the object and calls `glfs_fsync` when the last write was `FILE_SYNC4`, then closes the temporary fd.

## State and Persistence Behavior

The DS handle stores the GFAPI object handle, a lazy connection flag, and last write stability. Persistent effects are direct Gluster file data writes and fsyncs. Because writes bypass normal MDS object flow, the file explicitly triggers cache invalidation so Ganesha metadata does not remain stale.

## Dependencies and Integration Points

Dependencies include GFAPI handle/anonymous I/O functions, Ganesha pNFS DS default ops, Gluster export state, `op_ctx->ctx_pnfs_ds`, FSAL credential macros for commit open, and Gluster upcall invalidation. It is wired into the module through `pnfs_ds_ops_init`.

## Risks and Edge Cases

Stateid validation is not performed locally. `ds_write` returns the requested stability as achieved and only records it for later commit; error handling around partial writes depends on GFAPI return values. `ds_commit` only fsyncs when `stability_got == FILE_SYNC4`, which is unusual because unstable writes are typically the ones needing later commit. The wire handle validation is size-based and assumes the handle layout matches `struct glfs_ds_wire`. Temporary open/close failure handling can collapse into `NFS4ERR_INVAL`.

## Test Signals

Test signals include DS handle decode with valid and invalid sizes, read EOF and partial reads, write partial/error behavior, cache invalidation after DS writes, stable/unstable commit behavior, fsync error handling, GFAPI handle close on release, and pNFS integration with MDS export ids.
