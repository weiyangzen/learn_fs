# sources/storage-engines/foundationdb/fdbserver/workloads/LockDatabaseFrequently.cpp

## Purpose
Stress workload that repeatedly locks and unlocks the database to exercise lock system-key paths under frequent transitions.

## Important APIs, types, and functions
`LockDatabaseFrequentlyWorkload` has options `delayBetweenLocks` and `testDuration`, a `LockCount` counter, and actors `worker` and `lockAndUnlock`. It uses management helpers `lockDatabase(cx, uid)` and `unlockDatabase(cx, uid)`.

## Control flow
Only client 0 runs. The worker tracks Poisson schedules for lock and unlock phases, repeatedly creates a random UID, races lock completion with the next lock schedule, then races unlock completion with the next unlock schedule. It increments `lockCount` after each full cycle and returns once the duration timer is ready.

## State and persistence behavior
The workload continuously mutates the database lock system key state. It does not read or write user data and performs no explicit cleanup beyond each unlock operation.

## Dependencies and integration points
Depends on FoundationDB database lock management APIs, Flow Poisson pacing, and workload metrics.

## Risks and test signals
`check` always succeeds, so the workload is primarily a fault/exercise generator. Risks include overlapping lock timing semantics, disruption to unrelated workloads, and lock UID mismatch if helpers change. The signal is successful completion and the `LockCount` metric.
