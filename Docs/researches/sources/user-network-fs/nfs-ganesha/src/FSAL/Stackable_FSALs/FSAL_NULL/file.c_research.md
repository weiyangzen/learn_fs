<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/file.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/file.c

## Purpose

This file implements NULLFS file I/O object operations. It delegates close, open, read, write, seek, advise, commit, lock, close-state, and fallocate calls to the lower FSAL handle while preserving the stackable export context.

## Important APIs, Types, and Functions

- `struct null_async_arg`: records the NULLFS object, upper callback, and upper callback argument while an async lower-FSAL read/write is outstanding.
- `null_async_cb`: restores the upper export for the callback, invokes the original callback with the NULLFS object handle, restores the lower/current export, and frees the wrapper argument.
- `nullfs_close`: delegates old-style close.
- Multi-FD operations: `nullfs_open2`, `nullfs_check_verifier`, `nullfs_status2`, `nullfs_reopen2`, `nullfs_read2`, `nullfs_write2`, `nullfs_seek2`, `nullfs_io_advise2`, `nullfs_commit2`, `nullfs_lock_op2`, `nullfs_close2`, and `nullfs_fallocate`.

## Control Flow

Synchronous operations recover `nullfs_fsal_obj_handle` and `nullfs_fsal_export`, switch `op_ctx->fsal_export` to the lower export, call the lower handle's matching op, restore the NULL export, and return. `nullfs_open2` additionally wraps a returned lower `sub_handle` into a NULLFS handle with `nullfs_alloc_and_check_handle`. Async `read2` and `write2` allocate `null_async_arg`, call the lower FSAL with `null_async_cb`, and rely on the callback to translate the lower callback back into the upper NULLFS object context.

## State and Persistence Behavior

The file does not own persistent file data. It transiently allocates async callback wrappers and creates wrapper object handles when open-create returns a new lower object. State objects and file descriptors are lower-FSAL/SAL-owned and passed through unchanged.

## Dependencies and Integration Points

The code depends on `nullfs_methods.h` object/export wrappers, FSAL common multi-FD interfaces, access-check definitions, and lower FSAL `obj_ops`. It is installed into the NULLFS handle ops vector by `nullfs_handle_ops_init` in `handle.c`.

## Risks and Edge Cases

- Async callback correctness depends on `save_exp->super_export` being the right upper export when the lower callback fires.
- `nullfs_read2` and `nullfs_write2` allocate callback state unconditionally and do not handle allocation failure.
- If the lower FSAL completes async operations synchronously, `op_ctx` transitions still need to remain valid through `null_async_cb`.
- `nullfs_open2` only wraps when `sub_handle` is non-NULL. A lower FSAL that returns a handle with an error status would still be passed into `nullfs_alloc_and_check_handle`; that helper currently wraps only if status is success.

## Test Signals

Coverage should include read/write callback object identity, open-create returning a new object, reopen and close-state sequencing, fallocate pass-through, lock conflicts, and failure cases from lower FSAL methods. Async tests should confirm callback argument memory is freed and upper callbacks see the NULLFS handle, not the lower handle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/file.c -->
