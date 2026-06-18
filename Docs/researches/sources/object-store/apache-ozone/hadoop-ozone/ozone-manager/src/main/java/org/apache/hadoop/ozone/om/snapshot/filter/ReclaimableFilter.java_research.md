## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableFilter.java

Purpose: abstract base for GC filters that decide whether snapshot-related entries can be reclaimed after validating a stable view of the last N path snapshots.

Important APIs and types: implements Ratis `CheckedFunction<Table.KeyValue<String,V>, Boolean, IOException>` and `Closeable`. Key methods are `apply`, `initializePreviousSnapshotsFromChain`, `validateExistingLastNSnapshotsInChain`, `getLastNSnapshotInChain`, abstract `getVolumeName`, `getBucketName`, `isReclaimable`, and protected accessors for previous snapshots, bucket info, volume id, and key manager.

Control flow: `apply` extracts volume/bucket, checks whether the cached snapshot handles match the current chain and locks are held, opens/reopens the previous N snapshots in chain order under `SNAPSHOT_GC_LOCK`, loads active bucket and volume IDs, delegates to subclass logic, then validates the chain again before returning true. If the bucket or volume is already gone, entries are treated as reclaimable.

State and persistence: maintains cached previous snapshot infos and handles, locked snapshot IDs, bucket info, volume id, and reusable temporary lists. It does not write metadata but holds locks and snapshot references until closed or reinitialized.

Dependencies and integration: used by key, directory, and rename-entry reclaim filters. It integrates with `SnapshotChainManager`, `OmSnapshotManager`, `MultiSnapshotLocks`, active OM lock manager, `SnapshotUtils`, bucket manager, and key manager.

Risks and edge cases: `getLastNSnapshotInChain` calls `OmSnapshotManager.areSnapshotChangesFlushedToDB` even when `snapshotInfo` can become null; callers rely on that helper tolerating null or the loop can fail at chain start. Returning reclaimable for deleted buckets/volumes is intentional but high impact. Chain validation before and after subclass evaluation is essential; tests should simulate chain mutation, unflushed snapshot changes, lock acquisition failure, missing bucket/volume, current snapshot bucket mismatch, close cleanup, and ordering of locked snapshot IDs.
