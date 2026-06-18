# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_rename.c

## Purpose
Implements NFSv4 RENAME from SavedFH directory/oldname to CurrentFH directory/newname, enforcing same-export behavior and returning source and target directory change info.

## Important APIs, Types, and Functions
- `nfs4_op_rename` handles `NFS4_OP_RENAME`.
- Uses `nfs4_utf8string_scan`, `nfs4_sanity_check_FH`, `nfs4_sanity_check_saved_FH`, `nfs_get_grace_status`, `fsal_rename`, `fsal_get_changeid4`, and FSAL attr helpers.
- `nfs4_op_rename_Free` is a no-op.

## Control Flow
The handler validates both names as path components, verifies CurrentFH and SavedFH are directories, rejects cross-export renames with `NFS4ERR_XDEV`, gates mutation during grace, initializes source/target `before` change values, calls `fsal_rename`, then fills `source_cinfo` and `target_cinfo` from FSAL pre/post attrs or fallback changeids and sets atomic flags according to attr availability.

## State and Persistence Behavior
Mutates filesystem namespace across two directories. Reads SavedFH and CurrentFH but does not replace either handle. Returns cinfo for both old and new parent directories.

## Dependencies and Integration Points
Depends on SAVEFH/RESTOREFH-established saved directory state, FSAL rename semantics, export identity, grace management, and status conversion.

## Risks
The code computes post-change info even after `fsal_rename` returns an error because it does not branch before cinfo fill; callers must rely on status, but tests should ensure error responses do not expose misleading ok payloads. Same-export checks use export ids, not FSAL filesystem identity. Grace release must be balanced.

## Test Signals
Test same-directory and cross-directory rename, cross-export `XDEV`, invalid names, missing SavedFH, non-directory handles, grace rejection, FSAL failures, overwrites, and cinfo atomic combinations for one or both directories.
