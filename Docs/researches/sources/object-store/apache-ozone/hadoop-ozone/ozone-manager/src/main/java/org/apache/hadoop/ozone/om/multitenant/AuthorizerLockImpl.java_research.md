# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/AuthorizerLockImpl.java

## Purpose
`AuthorizerLockImpl` implements `AuthorizerLock` with a `StampedLock`. It serializes writes to the tenant authorizer and supports optimistic reads for read-mostly paths.

## Important APIs and Types
It implements all `AuthorizerLock` methods. Fields include the `StampedLock`, `omRequestWriteLockStamp`, and `omRequestWriteLockHolderTid`. Timeout wrappers use `OZONE_TENANT_AUTHORIZER_LOCK_WAIT_MILLIS` and throw `OMException` with `TIMEOUT` or `INTERNAL_ERROR`.

## Control Flow
`tryReadLock` and `tryWriteLock` delegate to `StampedLock.try*Lock(timeout, MILLISECONDS)`. `tryOptimisticReadThrowOnTimeout` first obtains a real read lock, converts it to an optimistic read stamp, and throws if either timed out or conversion unexpectedly fails. `tryWriteLockThrowOnTimeout` wraps interrupted waits and zero stamps. `tryWriteLockInOMRequest` obtains a write stamp, verifies no previous OM request write stamp is recorded, then stores stamp and thread id. `unlockWriteInOMRequest` tolerates missing stamp because a follower or leader change may mean no local lock was held; otherwise it clears fields and unlocks by stamp. `isWriteLockHeldByCurrentThread` compares the stored holder id with the current thread id.

## State and Persistence Behavior
State is process-local. It does not persist tenant changes; it guards the sequence in which OM requests and background authorizer synchronization interact with Ranger or in-memory access controllers.

## Dependencies and Integration Points
It integrates with `OMMultiTenantManagerImpl.AuthorizerOp`, OM tenant request classes, and authorizer background sync. It depends on Guava `Preconditions`, `StampedLock`, and OM exception result codes.

## Risks and Edge Cases
The stamp and holder fields are plain longs and are only safe because the code assumes they are updated while holding the write lock. `StampedLock` is not reentrant; repeated OM request write locking fails precondition checks. `unlockWriteInOMRequest` intentionally ignores zero stamps, which prevents follower paths from failing but can mask incorrect pairing if caller state is wrong.

## Test Signals
Tests should verify read/write timeout to `OMException`, optimistic read validation after a write, non-reentrant OM request write locks, holder thread checks, and zero-stamp unlock behavior after simulated follower/leader changes.
