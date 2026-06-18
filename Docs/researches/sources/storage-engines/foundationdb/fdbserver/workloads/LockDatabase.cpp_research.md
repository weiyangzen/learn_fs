# sources/storage-engines/foundationdb/fdbserver/workloads/LockDatabase.cpp

## Purpose
Database-lock correctness workload. It locks the database, verifies normal read-version requests fail while locked, then unlocks and checks user data did not change during the locked interval.

## Important APIs, types, and functions
`LockDatabaseWorkload` uses options `lockAfter`, `unlockAfter`, and `onlyCheckLocked`. Key actors are `lockAndSave`, `unlockAndCheck`, `checkLocked`, and `lockWorker`. It calls `lockDatabase`, `unlockDatabase`, reads `databaseLockedKey`, and uses transaction options `ACCESS_SYSTEM_KEYS`, `LOCK_AWARE`, and `READ_SYSTEM_KEYS`.

## Control flow
Client 0 either runs `checkLocked` for a bounded period or delays until `lockAfter`, locks using a random UID while reading all normal keys into a snapshot, starts a concurrent locked-state checker, waits until `unlockAfter`, cancels the checker, unlocks with the same UID, reads normal keys again, and compares both range results.

## State and persistence behavior
The workload writes database lock system state and reads normal key data for comparison. It does not change normal data itself. Unlock is skipped if the lock key is already absent.

## Dependencies and integration points
Depends on FoundationDB management lock helpers, system key permissions, normal-key range reads, lock-aware transactions, and read-version behavior while locked.

## Risks and test signals
Risks include assuming normal data fits in 50,000 rows, exact `RangeResult` comparison under concurrent workloads that may legitimately write unless coordinated, and cancellation of `checkLocked`. Signals are `GotVersionWhileLocked`, `DataChangedWhileLocked`, and final `ok`.
