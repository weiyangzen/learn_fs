<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_pathconf.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_pathconf.c

## Purpose
Implements NFSv3 `PATHCONF`, returning path configuration limits and booleans for the export containing the requested object.

## APIs, Types, and Functions
Exports `nfs3_pathconf()` and `nfs3_pathconf_free()`. It uses `PATHCONF3resok`, `struct fsal_export`, `op_ctx->fsal_export`, `nfs3_FhandleToCache()`, `nfs_SetPostOpAttr()`, and export attributes such as `maxread`, `maxwrite`, and hard-coded POSIX/NFS path configuration fields.

## Control Flow, State, and Persistence
The handler initializes failure object attributes to absent, resolves the object handle, then fills pathconf fields. It reports `linkmax` as `LINK_MAX`, `name_max` from `exp_hdl->exp_ops.fs_maxnamelen()`, `no_trunc = TRUE`, `chown_restricted = TRUE`, `case_insensitive = FALSE`, and `case_preserving = TRUE`. It includes post-op attributes and returns `NFS3_OK`. No persistent state changes occur.

## Dependencies and Integration
This operation depends on the active FSAL export selected during file-handle resolution and its `fs_maxnamelen` operation. It is integrated into the NFSv3 protocol surface as an export-level capability query rather than an object mutator.

## Risks and Test Signals
Risks include hard-coded case-sensitivity and chown semantics being wrong for unusual FSALs, name length changing by path or backend, and failure attributes being absent after handle errors. Test signals are PATHCONF on supported exports, backend-specific max name length checks, bad handle behavior, and clients relying on case or truncation fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_pathconf.c -->
