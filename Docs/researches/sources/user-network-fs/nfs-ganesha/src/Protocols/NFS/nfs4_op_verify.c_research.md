# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_verify.c

## Purpose
Implements NFSv4 VERIFY, comparing supplied attributes against the current object's attributes and returning OK, NOT_SAME, INVAL, or ATTRNOTSUPP.

## Important APIs, Types, and Functions
- `nfs4_op_verify` handles `NFS4_OP_VERIFY`.
- Uses `nfs4_sanity_check_FH`, `nfs4_Fattr_Check_Access`, `nfs4_Fattr_Supported`, `bitmap4_to_attrmask_t`, `file_To_Fattr`, `nfs4_Fattr_cmp`, `nfs4_Fattr_Free`, and FSAL attr helpers.
- `nfs4_op_verify_Free` is a no-op.

## Control Flow
The handler validates CurrentFH, checks requested attrs are readable and supported, converts the requested bitmap to an FSAL request mask, obtains current attributes into a generated `fattr4`, compares supplied and actual attrs, maps compare result `1` to OK, `-1` to INVAL, and all other mismatch to NOT_SAME, then frees generated fattr memory.

## State and Persistence Behavior
No state is changed. It reads object attributes and allocates temporary attribute structures.

## Dependencies and Integration Points
Depends on NFS attribute conversion/comparison and FSAL attribute retrieval through `file_To_Fattr`. It is part of compound conditional workflows that may gate later operations.

## Risks
Early returns after `fsal_prepare_attrs` but before `fsal_release_attrs` can leak attr resources if conversion or `file_To_Fattr` fails after allocation. Attribute comparison semantics must stay aligned with NFS VERIFY/NVERIFY protocol behavior.

## Test Signals
Test exact match, mismatch, unsupported attr, unreadable attr, invalid attr encoding, missing CurrentFH, attributes requiring allocated fattr memory, and cleanup under conversion/retrieval failure.
