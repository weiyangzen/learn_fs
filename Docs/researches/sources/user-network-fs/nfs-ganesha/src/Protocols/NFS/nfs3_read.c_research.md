<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_read.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_read.c

## Purpose
Implements NFSv3 `READ`, including synchronous and resumable asynchronous FSAL reads, export read limits, EOF compatibility handling, response data lifetime, and server I/O statistics.

## APIs, Types, and Functions
Key functions are `nfs3_read()`, `nfs3_complete_read()`, `nfs3_read_cb()`, `nfs3_read_resume()`, `nfs_read_ok()`, `read3_io_data_release()`, and `nfs3_read_free()`. It uses `struct nfs3_read_data`, `struct fsal_io_arg`, `fsal_read2()`, `obj->obj_ops->read2()`, `svc_resume()`, `resume_op_context()`, `server_stats_io_done()`, `gsh_calloc()`, and `nfs_SetPostOpAttr()`.

## Control Flow, State, and Persistence
The handler resolves the file handle, captures pre-op attributes, checks read access, rejects directories and non-regular/non-symlink reads, enforces `MaxRead` and `MaxOffsetRead`, handles zero-length reads locally, allocates an async data wrapper, and starts `fsal_read2()`. If the FSAL completes inline, `nfs3_complete_read()` sets `count`, `data`, `eof`, and attributes; if the FSAL returns async or resumable state, the request is suspended and later resumed via `rq_resume_cb`. For non-compliant EOF FSALs, completion may fetch file size to correct EOF at exact end. Persistent filesystem state is unchanged, but request state and object references persist while suspended.

## Dependencies and Integration
Depends on export options, FSAL read2 async contract, RPC suspend/resume infrastructure, op-context save/restore, XDR release callbacks for read buffers, and server statistics accounting. The file integrates tightly with `sal_functions.h` and object reference management.

## Risks and Test Signals
Risks include object or `read_data` lifetime bugs across async resume, incorrect EOF for FSALs without compliant EOF behavior, max-offset overflow checks, read buffer release ownership, and double statistics accounting on suspended paths. Test signals are zero-byte reads, reads past EOF, max read and max offset rejection, directory read `ISDIR`, async FSAL completion/resume, retryable errors, data buffer release, and stats counters for success/failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_read.c -->
