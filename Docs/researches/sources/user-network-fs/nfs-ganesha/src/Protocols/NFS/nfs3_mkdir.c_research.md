<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mkdir.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mkdir.c

## Purpose
Implements NFSv3 `MKDIR`, creating a directory under a parent directory handle and returning the new object's optional file handle, attributes, and parent weak cache consistency data.

## APIs, Types, and Functions
Exports `nfs3_mkdir()` and `nfs3_mkdir_free()`. It uses `MKDIR3args`, `MKDIR3resok`, `MKDIR3resfail`, `fsal_attrlist`, `nfs3_Sattr_To_FSALattr()`, `squash_setattr()`, `op_ctx->fsal_export->exp_ops.check_quota()`, `fsal_create()`, `nfs3_FSALToFhandle()`, `nfs_SetPostOpAttr()`, and `nfs_SetWccData()`.

## Control Flow, State, and Persistence
The handler prepares attributes for the new directory and parent WCC, resolves the parent handle, validates that the parent is a directory, checks inode quota, validates name and sattr conversion, applies credential squashing, and ensures a mode is present. It calls `fsal_create()` with type `DIRECTORY`, releases requested attributes, builds a post-op file handle, fills new-object attributes and parent WCC, and returns `NFS3_OK`. On failure it maps FSAL status and returns parent WCC if available.

## Dependencies and Integration
Integrated with export quota policy, credential squashing, FSAL create semantics, NFSv3 file-handle encoding, and mdcache reference lifetimes. Parent pre/post attributes are requested from the FSAL create call to satisfy NFSv3 WCC rules.

## Risks and Test Signals
Risks include defaulting missing mode to zero, quota checks happening before full name/attribute validation, inherited ACL or sattr release correctness, and file-handle allocation cleanup. Test signals are normal mkdir, empty name, non-directory parent, quota denial, invalid sattr, handle-encoding failure, parent WCC correctness, and `nfs3_mkdir_free()` freeing only successful returned handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mkdir.c -->
