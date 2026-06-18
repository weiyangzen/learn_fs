<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readlink.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readlink.c

## Purpose
Implements NFSv3 `READLINK`, returning the contents of a symbolic link and post-operation attributes for the link object.

## APIs, Types, and Functions
Exports `nfs3_readlink()` and `nfs3_readlink_free()`. It uses `READLINK3resok`, `READLINK3resfail`, `struct fsal_obj_handle`, `nfs3_FhandleToCache()`, `fsal_readlink()`, `nfs_SetPostOpAttr()`, `nfs3_Errno_status()`, and `gsh_free()` for the returned path buffer.

## Control Flow, State, and Persistence
The handler resolves the file handle, initializes failure attributes as absent, verifies the object is a symbolic link through FSAL behavior, calls `fsal_readlink()`, maps errors with retry/drop handling, and on success returns a dynamically allocated path string plus link attributes. It releases the object reference and frees the path only in `nfs3_readlink_free()` when status is `NFS3_OK`.

## Dependencies and Integration
Depends on FSAL symlink content retrieval and NFSv3 XDR ownership of the returned string. It integrates with attribute reporting and common retryable error policy.

## Risks and Test Signals
Risks include path buffer ownership mismatches, backend readlink size limits, non-symlink error mapping, and absent attributes on failure. Test signals are valid symlink reads, non-symlink handles, broken/stale handles, retryable backend errors, long symlink targets, and memory leak checks for successful response cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readlink.c -->
