# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_test_stateid.c

## Purpose
Implements NFSv4.1 TEST_STATEID, returning per-stateid validation status codes without failing the whole operation for individual invalid stateids.

## Important APIs, Types, and Functions
- `nfs4_op_test_stateid` handles `NFS4_OP_TEST_STATEID`.
- Uses `nfs4_Check_Stateid` with `STATEID_NO_SPECIAL`.
- Allocates `tsr_status_codes_val` with `gsh_calloc`.
- `nfs4_op_test_stateid_Free` frees the status-code array on success.

## Control Flow
The handler rejects minorversion 0, allocates an array sized to the number of input stateids, loops over each stateid, validates it without an object and without special stateids, releases any returned state ref, stores the returned `nfsstat4` in the output array, sets output length, and returns top-level OK.

## State and Persistence Behavior
Does not mutate persistent state. It temporarily obtains and releases state references during validation.

## Dependencies and Integration Points
Depends on SAL stateid lookup/validation and compound minorversion. It gives clients a batch state-validity probe for sessions.

## Risks
Input count directly drives allocation; very large requests rely on upstream XDR/request limits. Special stateids are intentionally not accepted. Free hook must run only when top-level status is OK and allocation occurred.

## Test Signals
Test v4.0 invalid, empty stateid list, valid open/lock/delegation stateids, stale/revoked/bad stateids, special all-zero/all-one stateids rejected, mixed result arrays, and cleanup of allocated status arrays.
