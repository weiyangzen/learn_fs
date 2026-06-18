## sources/storage-engines/foundationdb/fdbserver/workloads/RandomRangeLock.cpp

`RandomRangeLockWorkload` is a failure injection workload for exclusive read locks on random ranges. It registers randomly duplicated owner names, attempts to lock arbitrary byte ranges after random delays, holds successful locks briefly, unlocks them, and finally asserts that no locks remain for the workload's owner prefix.

Important APIs are `registerRangeLockOwner`, `getRangeLockOwner`, `takeExclusiveReadLockOnRange`, `releaseExclusiveReadLockOnRange`, `findExclusiveReadLockOnRange`, `RangeLockState`, and failure-injector hooks. The no-options constructor only enables injection when read range locks are enabled and incompatible version-vector/private mutation features are off; the options constructor enables in simulation on client 0.

Each `lockActor` chooses a duration and start delay, constructs an owner name from a prefix plus a random actor index, registers that owner, delays, generates a random range from random byte strings, and attempts to lock. `range_lock_failed` is expected for ranges beyond `normalKeys.end`; `range_lock_reject` is acceptable for conflicts. It then waits, attempts unlock, and accepts corresponding failed/rejected errors. `start` runs `lockActorCount` actors concurrently and verifies every owner prefix slot has no remaining locks in `normalKeys`.

State persists range lock owner and lock metadata in system keys. Runtime state includes randomized owners and lock ranges. Risks include duplicate owner names intentionally racing, random ranges outside normal keyspace, feature gating differing between constructors, and the workload's final cleanup only checking owner names in the configured prefix range. Failed registration or actor cancellation propagates.

Integration points are the range lock subsystem, system metadata, failure injection scheduler, and simulator. Test signals are assertions on owner presence, expected error codes, range bounds for failed locks, and final empty lock searches. `check` returns true after execution.
