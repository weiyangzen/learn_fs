<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_write.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_write.c

## Purpose
Implements NFSv3 `WRITE`, including export limits, stable/unstable write policy, quota checks, asynchronous FSAL write completion, WCC generation, write verifiers, and server I/O accounting.

## APIs, Types, and Functions
Key functions are `nfs3_write()`, `nfs3_complete_write()`, `nfs3_write_cb()`, `nfs3_write_resume()`, and `nfs3_write_free()`. It uses `struct nfs3_write_data`, `struct fsal_io_arg`, `obj->obj_ops->write2()`, `svc_resume()`, `resume_op_context()`, `server_stats_io_done()`, `NFS3_write_verifier`, `op_ctx->export_perms.options & EXPORT_OPTION_COMMIT`, `MaxWrite`, `MaxOffsetWrite`, and `nfs_SetWccData()`.

## Control Flow, State, and Persistence
The handler resolves the object, captures pre-op attributes, checks write access, rejects directories/non-regular objects, checks inode quota, validates count and max-offset limits, handles zero-length writes locally, allocates an async write wrapper, sets `fsal_stable` based on client stable mode or forced export commit, and calls `write2()`. Completion maps FSAL status, returns count, committed mode, verifier, and WCC, releases the object, frees wrapper state, and records I/O stats. Suspended FSAL operations persist request state until callback/resume.

## Dependencies and Integration
Depends on FSAL async write2 contract, export commit and write size configuration, quota checks, RPC suspend/resume, op-context restore, and global NFSv3 write verifier state. It is a major integration point for writeback semantics and statistics.

## Risks and Test Signals
Risks include stable write mode mismatches, quota type using inode quota for data writes, max-offset overflow, WCC after partial writes, async lifetime/double-free bugs, and stats accounting differences between inline and suspended writes. Test signals are unstable/data-sync/file-sync writes, forced commit exports, zero-byte writes, `FBIG` limits, async callback/resume, partial writes, verifier consistency across reboot policy, and WCC validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_write.c -->
