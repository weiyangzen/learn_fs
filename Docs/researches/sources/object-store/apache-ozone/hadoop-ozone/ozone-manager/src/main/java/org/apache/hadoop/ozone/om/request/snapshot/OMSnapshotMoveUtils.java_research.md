
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/snapshot/OMSnapshotMoveUtils.java

Purpose: Shared helper for snapshot move requests to update transaction metadata for source and destination snapshots.

Important APIs and types: Static utility class; uses `SnapshotInfo`, `TransactionInfo.valueOf(context.getTermIndex())`, `OmMetadataManagerImpl`, `snapshotInfoTable`, `CacheKey`, and `CacheValue`.

Control flow: `updateCache` loads the metadata manager, sets `lastTransactionInfo` on the source snapshot, adds it to snapshot info table cache, and repeats for the destination snapshot when non-null.

State and persistence behavior: Schedules snapshot info table cache updates at the current transaction index. It mutates the passed `SnapshotInfo` objects in place.

Dependencies and integration points: Used by deleted-key/table-key movement handlers so snapshot metadata reflects the move transaction.

Risks: Callers must ensure the `SnapshotInfo` objects are current and safe to mutate. Tests should verify source-only and source-plus-destination updates, correct term/index encoding, and cache keys.
