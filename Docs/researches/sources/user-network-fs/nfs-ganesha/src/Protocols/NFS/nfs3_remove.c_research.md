<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_remove.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_remove.c

## Purpose
Implements NFSv3 `REMOVE`, deleting a non-directory name from a parent directory and returning parent weak cache consistency data.

## APIs, Types, and Functions
Exports `nfs3_remove()` and `nfs3_remove_free()`. It uses `REMOVE3args`, `REMOVE3resok`, `REMOVE3resfail`, `fsal_lookup()`, `fsal_remove()`, `nfs3_FhandleToCache()`, `nfs_SetPreOpAttr()`, `nfs_SetWccData()`, `nfs_PreOpAttrFromFsalAttr()`, and FSAL attribute lists for parent pre/post state.

## Control Flow, State, and Persistence
The handler resolves the parent directory, captures pre-op attributes, validates directory type and non-empty name, optionally looks up the child to reject directories with `NFS3ERR_ISDIR`, then calls `fsal_remove()`. Success returns WCC from FSAL-provided parent pre/post attributes; failure maps FSAL status and returns failure WCC. The persistent effect is deletion through the FSAL when the remove succeeds.

## Dependencies and Integration
Integrated with FSAL namespace mutation, mdcache object references, and NFSv3 WCC. It relies on a pre-delete child lookup for protocol-specific directory rejection but still delegates final remove races to FSAL.

## Risks and Test Signals
Risks include lookup/remove races where a child changes type between validation and deletion, incomplete WCC if FSAL lacks pre/post attributes, and retryable error handling after partial backend mutation. Test signals are file removal, directory removal rejection, nonexistent name, empty name, non-directory parent, concurrent rename/remove races, and WCC validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_remove.c -->
