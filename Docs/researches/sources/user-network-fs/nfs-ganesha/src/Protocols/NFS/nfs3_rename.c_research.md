<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rename.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rename.c

## Purpose
Implements NFSv3 `RENAME`, moving or replacing an entry between two parent directories while enforcing export boundaries and returning WCC for both source and destination directories.

## APIs, Types, and Functions
Exports `nfs3_rename()` and `nfs3_rename_free()`. It uses `RENAME3args`, `RENAME3resok`, `RENAME3resfail`, `nfs3_FhandleToExportId()`, `nfs3_FhandleToCache()`, `fsal_rename()`, `nfs_SetPreOpAttr()`, `nfs_SetWccData()`, `nfs_PreOpAttrFromFsalAttr()`, and FSAL pre/post attribute lists for both directories.

## Control Flow, State, and Persistence
The handler rejects malformed or cross-export source/destination handles, resolves both parent directories, captures pre-op attributes, validates directory types and non-empty source/destination names, and invokes `fsal_rename()` with source and destination parent pre/post attributes. Success returns WCC for both directories; failure maps the FSAL status and still attempts to return WCC. Persistent state changes are entirely in the FSAL rename.

## Dependencies and Integration
Depends on export ID encoding in NFSv3 handles, FSAL atomic rename semantics, object reference management, and WCC helpers. It integrates with client-cache correctness by reporting both old and new directory changes.

## Risks and Test Signals
Risks include cross-export enforcement differing from backend mount boundaries, rename races with directory replacement rules, partial or non-atomic backend rename behavior, and WCC accuracy when source and destination directories are the same object. Test signals are same-directory rename, cross-directory rename, cross-export `XDEV`, empty names, non-directory parents, replacement cases, and same-parent WCC consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rename.c -->
