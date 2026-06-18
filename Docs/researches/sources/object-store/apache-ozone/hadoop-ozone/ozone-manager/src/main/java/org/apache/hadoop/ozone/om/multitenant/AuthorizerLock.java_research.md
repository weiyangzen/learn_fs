# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/multitenant/AuthorizerLock.java

## Purpose
`AuthorizerLock` defines the synchronization contract around the external multi-tenant authorizer, typically Ranger. It lets background sync and tenant OM requests coordinate reads, writes, and optimistic reads.

## Important APIs and Types
The interface exposes timed read/write acquisition (`tryReadLock`, `tryWriteLock`), stamped unlocks, optimistic read helpers, timeout-throwing wrappers, OM-request-specific write lock wrappers, and `isWriteLockHeldByCurrentThread`.

## Control Flow
Implementations return `StampedLock` stamps that callers must pass back to the matching unlock. `tryOptimisticReadThrowOnTimeout` is intended to block briefly for a read state, convert to optimistic read, and later allow validation. OM requests use `tryWriteLockInOMRequest` and `unlockWriteInOMRequest` so the implementation can remember ownership during request execution.

## State and Persistence Behavior
The interface itself has no state. It protects in-memory and remote authorizer state transitions; persistence of tenant metadata is handled elsewhere by OM request processing and the access controller backend.

## Dependencies and Integration Points
It is private/unstable and referenced by `OMMultiTenantManagerImpl.AuthorizerOp`. Concrete `AuthorizerLockImpl` uses `StampedLock`.

## Risks and Test Signals
Callers must pair stamps correctly or implementations may throw `IllegalMonitorStateException`. Tests should cover timeout behavior, optimistic read validation, and OM-request write lock ownership checks.
