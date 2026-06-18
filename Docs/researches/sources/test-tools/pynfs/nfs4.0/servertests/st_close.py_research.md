# sources/test-tools/pynfs/nfs4.0/servertests/st_close.py

## Purpose
`st_close.py` tests NFSv4 `CLOSE` behavior for normal created/opened files, sequence ID validation, bad/old/stale stateids, no-current-filehandle errors, lease expiry, lock release, and replay handling.

## Important APIs, Types, And Functions
- `testCloseCreate` and `testCloseOpen` validate ordinary close paths.
- `testBadSeqid`, `testBadStateid`, `testOldStateid`, `testStaleStateid`, and `testNoCfh` cover negative protocol cases.
- `testTimedoutClose1` and `testTimedoutClose2` sleep past lease time, force conflicting opens, and expect `NFS4ERR_EXPIRED`.
- `testReplaySeqid1`, `testNextSeqid`, and `testReplaySeqid2` exercise replay and next-seqid behavior, including multiple opens under the same owner.
- The module uses `makeStaleId` from `environment`.

## Control Flow
Tests initialize a client, create or open files with confirmed stateids, then call `close_file` with normal or manipulated seqid/stateid/current-fh arguments. Timeout tests sleep for twice the lease, use `env.c2` to force state cleanup through a conflicting write open, and then attempt CLOSE with the old state. Replay tests capture the sequence ID before CLOSE and repeat the request.

## State And Persistence Behavior
The module relies heavily on server open-owner state, lease timers, stateid sequence numbers, and replay caches. It creates temporary files in the test export and expects lock state to be released when close succeeds or state expires.

## Dependencies And Integration Points
It imports constants, `check`, and `makeStaleId`. It uses `NFS4Client` helpers for `init_connection`, `create_confirm`, `open_confirm`, `close_file`, `lock_file`, `get_seqid`, and lease-time queries.

## Risks And Edge Cases
- Timeout tests use real sleeps based on server-reported lease time, so they are slow and timing-sensitive.
- `testNextSeqid` intentionally does not assert a specific error after a replay with next seqid, only that the server does not crash.
- Stale stateid behavior depends on `makeStaleId`'s server-specific opaque stateid assumptions.

## Test Signals
Signals include `NFS4_OK`, `NFS4ERR_BAD_SEQID`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_STALE_STATEID`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_EXPIRED`, successful replayed CLOSE, and lock-release behavior after close.
