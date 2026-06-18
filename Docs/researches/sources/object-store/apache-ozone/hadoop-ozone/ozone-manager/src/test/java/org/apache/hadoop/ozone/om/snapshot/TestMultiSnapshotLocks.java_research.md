# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestMultiSnapshotLocks.java

Purpose: Tests `MultiSnapshotLocks`, the helper for acquiring/releasing write locks for multiple snapshot IDs. Important APIs and types include `IOzoneManagerLock`, `OzoneManagerLock.LeveledResource`, `SNAPSHOT_GC_LOCK`, `OMLockDetails`, `OMException`, and UUID collections.

Control flow: One test uses a real `OzoneManagerLock` and two `MultiSnapshotLocks` instances to repeatedly acquire/release different snapshot locks. Mock-based tests verify successful acquisition delegates once to `acquireWriteLocks`, failed acquisition clears internal state, release delegates to `releaseWriteLocks` and empties tracked locks, and attempting to acquire again before release throws an `OMException` with current lock IDs.

State and persistence behavior: State is in-memory lock ownership within `MultiSnapshotLocks`; there is no filesystem or DB state. Integration points are OM lock manager multi-resource APIs and snapshot GC locking resources.

Risks: Mock tests validate delegation and local state, not actual deadlock ordering beyond the real-lock smoke loop. Test signals are acquired flags, empty/non-empty object-lock set, verified acquire/release calls, and exact exception message for reentrant acquisition.
