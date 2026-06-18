# sources/object-store/minio/cmd/local-locker_test.go

## Purpose

`local-locker_test.go` validates the in-memory lock manager's expiration, read/write unlock, UID indexing, and force-unlock behavior under many locks and readers. It is the main safety net for `local-locker.go`.

## Important Tests And Control Flow

`TestLocalLockerExpire` creates 1000 write locks and 1000 read-locked resources, verifies `lockMap` and `lockUID` counts, runs a non-expiring cleanup, then expires everything with a negative interval and expects both maps empty. `TestLocalLockerUnlock` creates 1000 group write locks over five resources each plus read locks with two different UIDs, then releases one read UID, the second read UID, and all write locks while checking both map sizes after each phase. `Test_localLocker_expireOldLocksExpire` uses deterministic random data to create up to one million lock resources with varying reader counts, verifies cleanup keeps fresh locks, manually makes roughly half stale, then expires the rest. `Test_localLocker_RUnlock` similarly stresses force-unlocking a random half of read locks and regular `RUnlock` for the remainder.

The tests use `uuid`, deterministic `math/rand`, `hex` resource names, and `testing.Short` skips for the most expensive combinations.

## Risks And Test Signals

The tests strongly signal expected map cardinality and cleanup performance. They do not directly cover overload rejection, context cancellation while waiting, owner mismatch denial beyond the helper-level behavior, write/read conflict interleavings under concurrent goroutines, or refresh extending lock life. Still, the large deterministic cases are useful for catching UID-index leaks and slice-removal mistakes.
