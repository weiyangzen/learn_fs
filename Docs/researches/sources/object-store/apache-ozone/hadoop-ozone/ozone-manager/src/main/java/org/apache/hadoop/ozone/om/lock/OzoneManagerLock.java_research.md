# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneManagerLock.java

## Purpose
`OzoneManagerLock` is the central Ozone Manager concurrency primitive. It exposes the `IOzoneManagerLock` API over striped `ReentrantReadWriteLock` instances and enforces resource-ordering rules so OM requests do not acquire locks in cycles. It handles both the legacy numeric hierarchy represented by `LeveledResource` and a DAG resource family represented by `DAGLeveledResource`.

## Important APIs and Types
- Constructor `OzoneManagerLock(ConfigurationSource)` creates lock metrics and two resource maps: one for `LeveledResource` and one for `DAGLeveledResource`.
- Public lock APIs include `acquireReadLock`, `acquireReadLocks`, `acquireWriteLock`, `acquireWriteLocks`, `acquireResourceWriteLock`, and matching release methods.
- Multi-user helpers `acquireMultiUserLock` and `releaseMultiUserLock` acquire two `USER_LOCK` write locks through the bulk-lock path.
- Introspection/testing APIs include `getReadHoldCount`, `getWriteHoldCount`, `isWriteLockedByCurrentThread`, `getOMLockMetrics`, and `cleanup`.
- `LeveledResource` defines `S3_BUCKET_LOCK`, `VOLUME_LOCK`, `BUCKET_LOCK`, `USER_LOCK`, `S3_SECRET_LOCK`, `KEY_PATH_LOCK`, `PREFIX_LOCK`, and `SNAPSHOT_LOCK` with bit-mask ordering logic.

## Control Flow
Construction calls `getLeveledLocks` and `getFlatLocks`, each building an `EnumMap` from resource enum to a Guava-style `Striped<ReadWriteLock>`. Stripe count comes from `ozone.manager.striped.lock.size.<resource>` with a default; lock fairness is read from `OZONE_MANAGER_FAIR_LOCK`.

For single-key acquisition, `acquireLock` obtains the correct `ResourceLockTracker`, clears the per-thread `OMLockDetails`, checks `canLockResource`, finds a stripe by `CompositeKey.combineKeys(keys)`, locks either read or write side, updates wait metrics, and marks the resource locked in the tracker. Bulk acquisition uses `bulkGetLock` or `getAllLocks` and iterates in deterministic stripe order; release reverses the lock list before unlocking.

Unlock paths release the lock first and then update held-time metrics. For write unlock, the code captures `isWriteLockedByCurrentThread` before unlocking so metrics are recorded only for the owner’s final release. `updateProcessingDetails` sends timing to the current IPC call when available; for Ratis-applied writes where no `Server.Call` is present, it records wait/read/write timing into the tracker’s `OMLockDetails` so the response can carry lock timing back through the state machine.

## State and Persistence Behavior
The class does not persist state. Its mutable state is process-local: striped locks, `OMLockMetrics`, per-resource `ResourceManager` timing state, and tracker thread locals. Persistence integration is indirect: lock details are merged into OM responses and Ratis write execution, while lock ordering protects metadata cache and RocksDB update logic in request handlers.

## Dependencies and Integration Points
It integrates with `OMLockMetrics`, `ResourceLockTracker`, `LeveledResourceLockTracker`, `DAGResourceLockTracker`, `ResourceManager`, Hadoop IPC `ProcessingDetails`, and OM request classes that acquire bucket, volume, user, prefix, snapshot, and S3 locks. The `RegularBucketLockStrategy` delegates bucket locks to this class. Configuration is provided by `ConfigurationSource`.

## Risks and Edge Cases
The hierarchy is enforced per thread through trackers; callers that bypass the lock API or mix unrelated lock systems can still deadlock. Bulk locks ignore null key arrays in `bulkGetLock`, so callers must ensure input collections represent the intended locks. Reentrant acquisition is allowed for lower resources but deliberately forbidden for `USER_LOCK`, `S3_SECRET_LOCK`, and `PREFIX_LOCK` under the mask logic. Metrics start times live on enum resource managers, so correctness depends on the reentrancy checks preventing overwritten timing for nested holds.

## Test Signals
The file exposes `@VisibleForTesting` helpers for current locks and hold counts. Tests should verify hierarchy violations, allowed high-order acquisition, multi-user lock ordering, metrics timing on final release, read/write reentrancy behavior, and Ratis/no-IPC `OMLockDetails` propagation.
