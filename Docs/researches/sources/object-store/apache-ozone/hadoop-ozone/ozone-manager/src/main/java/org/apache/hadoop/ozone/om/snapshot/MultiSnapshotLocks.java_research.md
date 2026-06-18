# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/MultiSnapshotLocks.java

Purpose: `MultiSnapshotLocks` is a small lock helper for acquiring and releasing read or write locks over multiple snapshot IDs as one logical operation.

Important APIs and types: constructors accept an `IOzoneManagerLock`, lock `Resource`, read/write mode, and optional expected lock count. `acquireLock(Collection<UUID>)` maps UUIDs to one-element lock key arrays and delegates to `acquireWriteLocks()` or `acquireReadLocks()`. `releaseLock()` releases the recorded keys. Test-visible `getObjectLocks()` exposes held key arrays, and `isLockAcquired()` mirrors the latest lock details.

Control flow: `acquireLock()` is synchronized and refuses nested acquisition on the same helper instance by throwing `OMException(INTERNAL_ERROR)` if a lock is already recorded. Null IDs are filtered out. On successful acquisition, the helper records all key arrays and sets internal details to an acquired sentinel; otherwise it records not-acquired. `releaseLock()` releases exactly the recorded keys and clears them.

State and persistence behavior: no persistent state. Runtime state is the list of currently held lock keys and an `OMLockDetails` flag.

Dependencies and integration points: it wraps `IOzoneManagerLock` and is used by `SnapshotDeletingService` to lock a deleted snapshot and the next active snapshot before moving snapshot metadata. The caller is responsible for supplying IDs in chain-safe order to avoid deadlocks, as noted in local comments elsewhere.

Risks: if release is called without a successful acquire, it delegates with an empty key list; behavior depends on the lock implementation. The class records acquired state using empty sentinel lock details rather than the exact details returned by the underlying lock. Reusing one instance concurrently across unrelated operations is prevented by synchronization but still not a good ownership model.

Test signals: `TestMultiSnapshotLocks` validates multiple lock acquisition, nested acquisition errors, and read/write release behavior. Integration tests mock construction in snapshot deletion scenarios.
