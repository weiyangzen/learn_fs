# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/ReadOnlyHierarchicalResourceLockManager.java

## Purpose
`ReadOnlyHierarchicalResourceLockManager` is a no-op implementation of `HierarchicalResourceLockManager` for read-only contexts where mutation locks should never be acquired.

## Important APIs and Types
It returns two singleton anonymous `HierarchicalResourceLock` implementations: one reports `isLockAcquired() == true` for read locks and the other reports `false` for write/resource-write locks. `getCurrentLockedResources` returns an empty stream, and `close` is a no-op.

## Control Flow
`acquireReadLock` immediately returns the acquired empty handle without touching any shared state. `acquireWriteLock` and `acquireResourceWriteLock` return the non-acquired empty handle. The returned handles have empty `close` methods.

## State and Persistence Behavior
There is no state and no persistence. The class communicates capability via the returned lock status rather than blocking.

## Dependencies and Integration Points
It implements the same interface as the pool-based manager, letting read-only metadata readers plug into code expecting a hierarchical lock manager without changing call sites.

## Risks and Edge Cases
Callers must check `isLockAcquired` for write locks if they use this implementation. Any code that assumes `acquireWriteLock` always returns a successful handle could accidentally perform writes without synchronization, so this class should only be injected into strictly read-only paths.

## Test Signals
Tests should verify all methods are non-blocking, read locks report acquired, write locks report not acquired, and current locked resources is empty.
