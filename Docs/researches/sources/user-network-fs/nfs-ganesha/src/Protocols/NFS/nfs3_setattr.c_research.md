<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_setattr.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_setattr.c

## Purpose
Implements NFSv3 `SETATTR`, applying client-provided size/mode/owner/time updates with optional guarded ctime checking and returning object weak cache consistency data.

## APIs, Types, and Functions
Exports `nfs3_setattr()` and `nfs3_setattr_free()`. It uses `SETATTR3args`, `sattr3`, `guard3`, `fsal_attrlist`, `nfs3_Sattr_To_FSALattr()`, `squash_setattr()`, `fsal_setattr()`, `state_deleg_conflict()`, `nfs_SetPreOpAttr()`, `nfs_SetWccData()`, and `sal_functions.h`.

## Control Flow, State, and Persistence
The handler resolves the object, captures pre-op attributes, optionally compares the guard ctime with current attributes and returns `NFS3ERR_NOT_SYNC` on mismatch, converts NFSv3 attributes to FSAL attributes, applies credential squashing when owner/group are set, checks for delegation conflict before mutating, and calls `fsal_setattr()`. Success and stable failures both return WCC based on pre and current post attributes; retryable errors are dropped. Persistent metadata changes occur through FSAL setattr, including possible truncation.

## Dependencies and Integration
Depends on attribute conversion policy, delegation conflict detection, export/user credential squashing, FSAL setattr semantics, and NFSv3 WCC. It integrates with state management by refusing changes while conflicting delegations exist.

## Risks and Test Signals
Risks include guard timestamp precision mismatches, owner/group squashing surprises, delegation conflict returning `JUKEBOX`, truncation/state interactions, and failure WCC accuracy. Test signals are guarded and unguarded mode/size/time changes, stale guard rejection, delegation conflict, invalid sattr conversion, retryable FSAL failures, and WCC before/after verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_setattr.c -->
