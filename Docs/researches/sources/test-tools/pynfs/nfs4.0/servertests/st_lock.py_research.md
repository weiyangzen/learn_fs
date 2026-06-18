# sources/test-tools/pynfs/nfs4.0/servertests/st_lock.py

## Purpose
`st_lock.py` is the main NFSv4 `LOCK` test module. It exercises basic locking, close interactions, existing-file opens, range size, overlapping lock merge/split, lock upgrade/downgrade, open-mode checks, invalid ranges, missing filehandles, sequence IDs, old/stale/bad stateids, client ID freshness, lease timeout cleanup, inter-owner and inter-client conflicts, read-lock coexistence, blocking-lock fairness/polling, lockowner reuse ideas, and open/lock/open-downgrade sequences.

## Important APIs, Types, And Functions
- `testFile`, `testClose`, `testExistingFile`, `test32bitRange`, `testOverlap`, `testDowngrade`, `testUpgrade`, `testMode`, `testZeroLen`, and `testLenTooLong` cover core lock semantics.
- `testNoFh`, `testBadLockSeqid`, `testBadOpenSeqid`, `testNonzeroLockSeqid`, `testOldLockStateid`, `testOldOpenStateid`, `testOldOpenStateid2`, `testStaleClientid`, `testBadStateid`, `testBadStateidganesha`, `testStaleLockStateid`, and `testStaleOpenStateid` cover protocol validation.
- `testTimedoutGrabLock`, `testGrabLock1`, `testGrabLock2`, `testReadLocks1`, and `testReadLocks2` cover lease expiry and conflict behavior.
- `testFairness`, `testBlockPoll`, `testBlockTimeout`, `testBlockingQueue`, and `testLongPoll` probe blocking lock queue/fairness semantics.
- `open_sequence` encapsulates open/downgrade/close/lock/unlock state for `testOpenUpgradeLock`.
- `testOpenDowngradeLock` and `testOpenUpgradeLock` combine open share transitions with lock operations.

## Control Flow
Most tests initialize a connection, create or open a confirmed file, acquire a lock with `lock_file`, then issue `lock_test`, `relock_file`, `unlock_file`, `downgrade_file`, or second-client/second-owner operations. Sequence and stateid tests deliberately pass bad sequence numbers, old stateids, all-zero stateids, Ganesha-specific bad IDs, or stale IDs. Timeout and blocking tests sleep for fractions or multiples of the lease time and poll or renew to shape server state.

Blocking-lock tests use write-wait lock types (`WRITEW_LT`) and expect denied responses while another owner holds a conflicting lock, then check fairness by attempting to let later owners steal the lock. The module also contains an indented block of older method-style tests under `testLockowner2`; those are not normal top-level tests.

## State And Persistence Behavior
This module creates many server-side open, lock, lockowner, and share states. It relies on stateids and lock state persisting across operations, owners, clients, sequence IDs, and lease intervals. It also depends on server cleanup when clients expire and on close releasing locks or returning `NFS4ERR_LOCKS_HELD`.

## Dependencies And Integration Points
Imports include NFS constants, `stateid4`, `check`, `get_invalid_clientid`, `makeStaleId`, `makeBadIDganesha`, `time`, and `nfs_ops`. It depends on extensive `NFS4Client` helper methods and environment lease timing.

## Risks And Edge Cases
- Real-time sleeps make lease and fairness tests slow and sensitive to server timing.
- Some checks accept alternate statuses or convert behavior to support warnings, especially 64-bit ranges, lock consolidation, atomic upgrades/downgrades, and closing locked files.
- Stateid mutation helpers are server-specific.
- Several owner strings are plain strings while much of the framework uses bytes; compatibility depends on client helper normalization.
- The older nested lockowner tests are likely not discovered and include outdated APIs.

## Test Signals
Signals include OK lock acquisition, `NFS4ERR_DENIED` for conflicts, denied lock owner details from LOCKT, `NFS4ERR_LOCK_RANGE`, `NFS4ERR_LOCK_NOTSUPP`, `NFS4ERR_OPENMODE`, `NFS4ERR_INVAL`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_BAD_SEQID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_STALE_CLIENTID`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, lease-expiry lock cleanup, and fairness warnings.
