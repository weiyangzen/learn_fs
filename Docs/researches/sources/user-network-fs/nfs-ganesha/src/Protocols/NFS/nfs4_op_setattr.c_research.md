# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setattr.c

## Purpose
Implements NFSv4 SETATTR, converting requested NFS attributes to FSAL attributes, enforcing writeability/support/stateid rules, gating mutations during grace, and applying the attributes through `fsal_setattr`.

## Important APIs, Types, and Functions
- `nfs4_op_setattr` handles `NFS4_OP_SETATTR`.
- Uses `nfs4_sanity_check_FH`, `nfs_get_grace_status`, `nfs4_Fattr_Check_Access`, `nfs4_Fattr_Supported`, `nfs4_Fattr_To_FSAL_attr`, `nfs4_Check_Stateid`, `squash_setattr`, `fsal_setattr`, and FSAL attr release.
- `nfs4_op_setattr_Free` is a no-op.

## Control Flow
The handler validates CurrentFH, rejects during grace, checks that requested attrs are writable and supported, converts them to an FSAL attrlist, and when size or space reservation is being set, rejects directories/non-regular files, validates the stateid, resolves open state from share/lock/delegation state, and requires write open access when an open state applies. It validates nanosecond ranges, squashes owner/group changes for squashed credentials, calls `fsal_setattr`, releases attrs, and returns the original attrmask in `attrsset` on success.

## State and Persistence Behavior
Mutates filesystem metadata and possibly file size through the FSAL. It only mutates NFS state by taking and releasing state refs during validation. Owner/group attributes may be transformed by credential squashing before persistence.

## Dependencies and Integration Points
Depends on NFS attribute conversion helpers, FSAL metadata mutation, SAL state validation, grace-state management, credential squashing, and CurrentFH object/filetype tracking.

## Risks
The function calls `nfs_put_grace_status` at the common `done` label even for failures before a successful grace reservation in some paths; this relies on grace helper semantics and deserves regression coverage. Size changes require correct open-mode enforcement across share, lock, delegation, and special stateids. Attribute conversion may allocate nested structures that must be released on every path after conversion.

## Test Signals
Test unsupported attrs, read-only attrs, invalid time nanoseconds, owner/group squashing, size truncate with read-only open, size on directory/non-file, special stateids, lock/delegation stateids, grace rejection, FSAL errors, ACL release, and `attrsset` echo on success.
