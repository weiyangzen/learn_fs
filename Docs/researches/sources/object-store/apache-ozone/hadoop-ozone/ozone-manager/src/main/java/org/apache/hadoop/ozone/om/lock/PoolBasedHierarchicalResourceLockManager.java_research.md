# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/PoolBasedHierarchicalResourceLockManager.java

## Purpose
`PoolBasedHierarchicalResourceLockManager` implements `HierarchicalResourceLockManager` for DAG-style resources using a bounded Apache Commons pool of reusable `ReadWriteLock` objects. It provides key-level read/write locks and whole-resource write locks while enforcing DAG resource-ordering through `DAGResourceLockTracker`.

## Important APIs and Types
- Constructor reads soft and hard lock-pool limits from `OZONE_OM_HIERARCHICAL_RESOURCE_LOCKS_*` config keys.
- `acquireReadLock(DAGLeveledResource, String)` and `acquireWriteLock(...)` return closeable `HierarchicalResourceLock` handles.
- `acquireResourceWriteLock(DAGLeveledResource)` locks the resource-level write lock, blocking all key-level locks for that resource.
- `getCurrentLockedResources` delegates to the resource tracker.
- Inner `PoolBasedHierarchicalResourceKeyLock` and `PoolBasedHierarchicalResourceLock` own lifecycle and release on `close`.
- `LockReferenceCountPair` associates a pooled lock with a reference count.

## Control Flow
The manager keeps, per `DAGLeveledResource`, a resource-level `ReentrantReadWriteLock` plus a concurrent map from string key to `LockReferenceCountPair`. Key-lock acquisition first checks `resourceLockTracker.canLockResource`; then `operateOnLock` atomically computes the key map entry, borrowing a lock from the pool if needed and incrementing the reference count. The returned lock handle acquires the resource-level read lock and then the key lock. Whole-resource acquisition takes the resource-level write lock instead.

On `close`, a key lock unlocks the key lock, unlocks the resource-level read lock, updates the tracker, and decrements the reference count through `operateOnLock`. When the count reaches zero, the pooled `ReadWriteLock` is returned and the key entry is removed. The whole-resource lock only unlocks the resource write lock and tracker state.

## State and Persistence Behavior
All state is in-memory: pool contents, per-resource maps, reference counts, and tracker thread locals. There is no direct persistence. Its role is to protect hierarchical metadata operations, especially DAG-like structures such as filesystem trees or snapshot chains, before request handlers mutate OM metadata caches and RocksDB tables.

## Dependencies and Integration Points
It depends on Commons Pool `GenericObjectPool`, Ratis `UncheckedAutoCloseable`, `DAGLeveledResource`, `DAGResourceLockTracker`, and `OzoneConfiguration`. Callers are expected to use try-with-resources or otherwise close returned handles; failure to close leaks references and keeps lock objects checked out.

## Risks and Edge Cases
The key-level constructor increments reference count before acquiring the actual lock. If thread interruption or runtime failure occurs between construction steps, cleanup depends on handle close. `operateOnLock` returns pooled locks to the pool while inside a `ConcurrentHashMap.compute` callback; pool errors are wrapped into `IOException`. Whole-resource and key-level locking rely on the resource read/write lock ordering: resource write waits for all key read holders. Deadlock prevention is only as strong as `DAGResourceLockTracker`.

## Test Signals
Useful tests include pool limit exhaustion behavior, reference count increment/decrement and removal, whole-resource exclusion of key locks, close idempotence, tracker ordering rejection, and exception propagation when pool borrow fails.
