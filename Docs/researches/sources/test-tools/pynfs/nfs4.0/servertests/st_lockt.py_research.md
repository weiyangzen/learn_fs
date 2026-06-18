# sources/test-tools/pynfs/nfs4.0/servertests/st_lockt.py

## Purpose
`st_lockt.py` tests NFSv4 `LOCKT`, the non-mutating byte-range lock test operation. It covers unlocked files, non-file object types, partial locked ranges, 64-bit ranges, overlapping lock reports, invalid zero/overflow lengths, missing filehandle, and stale client IDs.

## Important APIs, Types, And Functions
- `testUnlockedFile` verifies LOCKT succeeds on an unlocked regular file.
- `testDir`, `testFifo`, `testLink`, `testBlock`, `testChar`, and `testSocket` validate errors for non-regular object types.
- `testPartialLockedFile1` and `testPartialLockedFile2` create locks and test overlapping/non-overlapping ranges.
- `test32bitRange`, `testOverlap`, `testZeroLen`, `testLenTooLong`, `testNoFh`, and `testStaleClientid` cover boundary and protocol errors.

## Control Flow
Tests initialize a client, create/confirm files where needed, and call `c.lock_test` directly or after creating locks via `c.lock_file`. Non-file tests call `lock_test` on environment paths. Range tests inspect status and, for overlap, the denied range reported in the response.

## State And Persistence Behavior
LOCKT itself should not mutate lock state, but many tests create locks first to observe conflict reporting. The module uses existing environment objects and temporary files.

## Dependencies And Integration Points
It imports NFS constants, `check`, and `get_invalid_clientid`. It relies on `NFS4Client.lock_test`, `lock_file`, `create_confirm`, environment paths, and client ID state.

## Risks And Edge Cases
- Expected status for symlink/non-file cases allows some variance, such as `NFS4ERR_SYMLINK`.
- 64-bit range support can return `NFS4ERR_BAD_RANGE` and be treated as unsupported.
- Stale client ID uses `get_invalid_clientid()` returning zero, which is a heuristic.

## Test Signals
Signals include OK LOCKT for unlocked/non-conflicting ranges, `NFS4ERR_DENIED` with correct denied range/type/owner for conflicts, `NFS4ERR_ISDIR` or `NFS4ERR_INVAL` for non-files, `NFS4ERR_INVAL` for zero length or overflow, `NFS4ERR_NOFILEHANDLE`, and `NFS4ERR_STALE_CLIENTID`.
