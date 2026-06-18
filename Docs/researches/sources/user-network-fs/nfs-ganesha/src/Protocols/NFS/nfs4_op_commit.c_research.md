<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_commit.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_commit.c

## Purpose
Implements NFSv4 `OP_COMMIT`, flushing unstable writes for a byte range and returning the export write verifier. It also supports pNFS data-server commit handles.

## APIs, Types, and Functions
Exports `nfs4_op_commit()` and `nfs4_op_commit_Free()`, with internal `op_dscommit()`. It uses `COMMIT4args/res`, `nfs4_Is_Fh_DSHandle()`, `nfs4_sanity_check_FH(REGULAR_FILE, true)`, `fsal_commit()`, `op_ctx->fsal_export->exp_ops.get_write_verifier()`, `op_ctx->ctx_pnfs_ds->s_ops.dsh_commit()`, and `nfs4_Errno_status()`.

## Control Flow, State, and Persistence
The handler initializes status, logs offset/count, dispatches directly to `op_dscommit()` for data-server file handles, otherwise validates the current FH as a regular file, calls `fsal_commit()` for the requested byte range, and fills the NFSv4 verifier from the active export. The data-server branch bypasses mdcache and calls the pNFS DS commit operation with `current_ds`. The operation persists data by forcing backend writeback/commit; no protocol state is otherwise changed.

## Dependencies and Integration
Depends on FSAL commit semantics, pNFS data-server context, export write verifier generation, and current FH/object setup. The compound table requires metadata write access before dispatch.

## Risks and Test Signals
Risks include verifier mismatch between MDS and DS paths, missing regular-file validation for DS handles, backend partial commit behavior, and stale `current_ds` context. Test signals are COMMIT after unstable writes, zero-count commit, commit past EOF, FSAL commit failure mapping, pNFS DS commit, verifier stability across normal operation, and verifier change after server restart policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_commit.c -->
