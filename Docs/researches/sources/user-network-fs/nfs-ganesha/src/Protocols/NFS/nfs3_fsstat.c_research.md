<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsstat.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsstat.c

## Purpose
Implements the NFSv3 `NFSPROC3_FSSTAT` handler. It translates a client file handle into an FSAL object, asks the FSAL/export for dynamic filesystem statistics, and returns NFSv3 filesystem byte/file counters plus post-operation attributes.

## APIs, Types, and Functions
The exported entry points are `nfs3_fsstat()` and `nfs3_fsstat_free()`. Important types are `fsal_dynamicfsinfo_t`, `fsal_status_t`, `struct fsal_obj_handle`, `FSSTAT3resok`, and `FSSTAT3resfail`. Core helper dependencies are `nfs3_FhandleToCache()`, `fsal_statfs()`, `nfs_SetPostOpAttr()`, `nfs3_Errno_status()`, `nfs_RetryableError()`, and object `put_ref`.

## Control Flow, State, and Persistence
The handler initializes failure post-op attributes to not-follow, logs the request, resolves the root file handle, calls `fsal_statfs()`, and maps retryable FSAL errors to `NFS_REQ_DROP` while stable failures become NFSv3 status codes. On success it copies `total_bytes`, `free_bytes`, `avail_bytes`, `total_files`, `free_files`, and `avail_files`, sets `invarsec` to zero to advertise volatile filesystem statistics, and returns `NFS3_OK`. State is request-local except for references acquired from the object cache and export context; no persistent metadata is changed.

## Dependencies and Integration
Integrated through the NFSv3 dispatch table and the shared protocol conversion/cache helpers. It depends on the current `op_ctx` populated by file-handle resolution, FSAL statfs support for the backing export, NFSv3 XDR result structs, logging, and attribute conversion helpers.

## Risks and Test Signals
Risks include stale or missing post-op attributes on error, incorrect retry/drop classification, FSALs returning dynamic counters in units not expected by NFSv3 clients, and `invarsec = 0` forcing clients to treat stats as volatile. Test signals are `FSSTAT` against valid and stale handles, retryable FSAL fault injection, statfs values matching backend capacity, and reference leak checks around object cache lookup failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsstat.c -->
