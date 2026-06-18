<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_getattr.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_getattr.c

## Purpose
Implements NFSv3 `GETATTR`, returning the full NFSv3 attribute set for a file handle by delegating to the FSAL object's `getattrs` operation.

## APIs, Types, and Functions
The file exports `nfs3_getattr()` and `nfs3_getattr_free()`. It works with `nfs_arg_t`, `nfs_res_t`, `struct fsal_attrlist`, and `struct fsal_obj_handle`. Important helpers are `fsal_prepare_attrs(ATTRS_NFS3)`, `nfs3_FhandleToCache()`, `obj->obj_ops->getattrs()`, `fsal_release_attrs()`, `nfs3_Errno_status()`, and `nfs_RetryableError()`.

## Control Flow, State, and Persistence
The handler prepares the response attribute list, resolves the input file handle, calls `getattrs`, maps errors, and sets `NFS3_OK` when attributes are available. Retryable backend failures drop the RPC for client retry; nonretryable failures are encoded in the protocol status. All state is transient: prepared attributes are released and the object reference is returned in all paths.

## Dependencies and Integration
This is a simple bridge between the NFSv3 dispatch layer and the FSAL/mdcache attribute path. It relies on `ATTRS_NFS3` selecting the correct protocol-visible attribute mask and on the XDR layer using the populated `GETATTR3res_u.resok.obj_attributes` directly.

## Risks and Test Signals
Risks include missing `fsal_release_attrs()` for attributes containing ACL or inherited data, stale cache attributes from FSAL implementations, and ambiguity between dropped retryable requests and protocol error returns. Test signals are attribute parity with backend stat data, stale/bad handle behavior, retryable error injection, and leak checks on repeated `GETATTR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_getattr.c -->
