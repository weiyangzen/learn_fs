<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rmdir.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rmdir.c

## Purpose
Implements NFSv3 `RMDIR`, removing a directory entry after verifying the parent is a directory and the named child is itself a directory.

## APIs, Types, and Functions
Exports `nfs3_rmdir()` and `nfs3_rmdir_free()`. It uses `RMDIR3args`, `RMDIR3resok`, `RMDIR3resfail`, `nfs3_FhandleToCache()`, `fsal_lookup()`, `fsal_remove()`, `nfs_SetPreOpAttr()`, `nfs_SetWccData()`, and parent pre/post `fsal_attrlist` values.

## Control Flow, State, and Persistence
The handler resolves the parent, captures pre-op attributes, validates parent type and non-empty name, looks up the child to ensure it is a directory, and calls `fsal_remove()` to remove it. Success returns parent WCC and `NFS3_OK`; failure maps FSAL status and returns failure WCC if possible. The only persistent mutation is the FSAL remove.

## Dependencies and Integration
Integrated with FSAL lookup/remove, object cache references, and NFSv3 WCC. It mirrors `REMOVE` with inverted type validation and relies on backend semantics for non-empty directory errors.

## Risks and Test Signals
Risks include child type races between lookup and remove, backend error mapping for non-empty directories, incomplete WCC, and retry/drop behavior after ambiguous backend failures. Test signals are empty directory removal, non-empty directory error, file removal rejected as `NOTDIR`, empty name, non-directory parent, and concurrent mutation tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rmdir.c -->
