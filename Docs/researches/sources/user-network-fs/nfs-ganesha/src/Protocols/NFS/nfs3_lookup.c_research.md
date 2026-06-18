<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_lookup.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_lookup.c

## Purpose
Implements NFSv3 `LOOKUP`, resolving a name within a directory file handle and returning the child file handle plus child and parent post-operation attributes.

## APIs, Types, and Functions
Exports `nfs3_lookup()` and `nfs3_lookup_free()`. It uses `LOOKUP3args`, `LOOKUP3resok`, `LOOKUP3resfail`, `struct fsal_attrlist`, `fsal_lookup()`, `nfs3_FhandleToCache()`, `nfs3_FSALToFhandle()`, `nfs_SetPostOpAttr()`, `nfs3_Errno_status()`, and `gsh_free()` for the dynamically allocated file-handle buffer.

## Control Flow, State, and Persistence
The handler prepares optional NFSv3 attributes with `ATTR_RDATTR_ERR`, initializes failure directory attributes to absent, resolves the directory handle, and calls `fsal_lookup()`. On lookup failure it maps status and returns directory attributes when possible. On success it builds an NFSv3 file handle for the child, fills child and directory attributes, and returns `NFS3_OK`; if file-handle construction fails, it reports `NFS3ERR_BADHANDLE`. The only persistent effect is cache lookup/reference activity; it does not mutate filesystem state.

## Dependencies and Integration
This is a core NFSv3 namespace operation and depends on the FSAL lookup path, export file-handle encoding, and attribute conversion. It integrates with the XDR free path through `nfs3_lookup_free()`, which releases the allocated handle only on successful lookup.

## Risks and Test Signals
Risks include leaked handle buffers if success status and allocation state diverge, ambiguous behavior for invalid names delegated to FSAL, and parent post-op attributes not representing the lookup instant. Test signals are successful lookup for files/directories/symlinks, nonexistent names, bad parent handles, file-handle encoding failure injection, and memory checks across repeated lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_lookup.c -->
