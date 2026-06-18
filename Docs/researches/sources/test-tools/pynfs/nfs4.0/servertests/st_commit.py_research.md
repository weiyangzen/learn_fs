# sources/test-tools/pynfs/nfs4.0/servertests/st_commit.py

## Purpose
`st_commit.py` tests the NFSv4 `COMMIT` operation on regular files and invalid current filehandle/object cases. It focuses on offset/count boundary behavior, non-regular object errors, no filehandle behavior, and overflow validation.

## Important APIs, Types, And Functions
- `_commit(t, c, offset=0, count=0, statlist=[NFS4_OK])` creates and confirms a file, writes `_text` with `UNSTABLE4`, then commits a specified range and checks allowed statuses.
- `testCommitOffset0`, `testCommitOffset1`, `testCommitOffsetMax1`, `testCommitOffsetMax2`, `testCommitCount1`, and `testCommitCountMax` exercise range boundaries.
- `testLink`, `testBlock`, `testChar`, `testDir`, `testFifo`, and `testSocket` commit against non-regular objects and expect type-specific errors.
- `testNoFh` sends COMMIT without a current filehandle.
- `testCommitOverflow` covers offset-plus-count overflow.

## Control Flow
Most tests call `_commit`, which sets up file state and delegates range-specific assertions. Non-regular tests use environment object paths and client commit helpers. The helper checks write success before issuing COMMIT so failures are isolated to COMMIT semantics.

## State And Persistence Behavior
The tests create temporary files and write unstable data before COMMIT. No local persistent state is maintained. For RAM-backed test servers, COMMIT may be a verifier-only no-op, but the protocol result remains observable.

## Dependencies And Integration Points
It imports NFS constants and `check`. It depends on `NFS4Client` methods `create_confirm`, `write_file`, `commit_file`, and environment paths for file types.

## Risks And Edge Cases
- The helper default `statlist=[NFS4_OK]` is a mutable default but not mutated.
- Maximum offset/count tests allow either OK or `NFS4ERR_INVAL`, acknowledging server variability.
- The local Python server treats commits as FILE_SYNC and does not implement durable storage, so these tests only validate protocol handling, not actual disk flushes.

## Test Signals
Signals are successful COMMIT on regular files, acceptable handling of maximum ranges, `NFS4ERR_ISDIR` or `NFS4ERR_INVAL` for non-regular objects, `NFS4ERR_NOFILEHANDLE` without cfh, and overflow rejection.
