## sources/storage-engines/foundationdb/fdbserver/workloads/RangeLock.cpp

`RangeLocking` is a deterministic client workload for the range lock subsystem. It registers a test owner, performs random lock/unlock and key-value operations, maintains in-memory models of locked ranges and visible KVS state, compares both models against database state, then tests releasing locks by owner across many owners.

Important APIs and types include `registerRangeLockOwner`, `takeExclusiveReadLockOnRange`, `releaseExclusiveReadLockOnRange`, `releaseExclusiveReadLockByUser`, `findExclusiveReadLockOnRange`, `RangeLockState`, `KeyRangeMap<bool>`, `coalesceRangeList`, and `FDBTransactionOptions::LOCK_AWARE`. `KVOperation` and `LockRangeOperation` record the random operations applied during each iteration.

The workload disables `RandomRangeLock` because both would race on lock state. `complexTest` loops up to 100 iterations, randomly updating locks and then DB keys. `updateLockMapWithRandomOperation` applies lock/unlock requests and records only accepted operations. `updateDBWithRandomOperations` tries random sets or range clears and accepts `transaction_rejected_range_locked` as expected. The memory model applies KV operations only if they do not intersect a locked range. `checkLockCorrectness` compares coalesced DB locks to the in-memory lock map; `checkKVCorrectness` reads normal keys with `LOCK_AWARE` and compares to the in-memory map. At the end it releases all locks for the main owner and asserts none remain.

`testUnlockByUser` registers 100 owners, tries to lock up to two random ranges each, randomly chooses users to unlock, calls `releaseExclusiveReadLockByUser`, and verifies unlocked users have no locks while other users still have exactly their coalesced lock ranges.

Persistent state includes lock owner metadata, lock records, and test keys in the small digit keyspace. Risks include `check` returning true regardless of the `pass`/`shouldExit` model flags, random lock conflicts causing skipped operations, reliance on normal keyspace filtering, and broad cleanup only for owners created in the workload. The workload intentionally uses `LOCK_AWARE` reads for validation so locks do not block model inspection.

Integration points are range lock metadata, transaction rejection for locked ranges, audit utilities, and management/system data. Test signals are assertions, `shouldExit` being set on mismatches, detailed `RangeLockWorkLoadHistory` trace events, and final empty-lock assertions.
