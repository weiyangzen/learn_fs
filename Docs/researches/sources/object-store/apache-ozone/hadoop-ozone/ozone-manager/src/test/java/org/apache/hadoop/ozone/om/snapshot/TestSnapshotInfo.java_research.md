# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotInfo.java

## Purpose
`TestSnapshotInfo` validates the OM metadata table for `SnapshotInfo` rows and helper methods that determine whether snapshot create/change transactions have flushed to DB.

## Important APIs, Types, and Functions
- `OMMetadataManager.getSnapshotInfoTable()` stores `SnapshotInfo`.
- `SnapshotInfo.Builder` sets identity, volume, bucket, status, creation/deletion times, previous snapshot ids, and path.
- `SnapshotInfo.setSstFiltered`, `isSstFiltered`, `setLastTransactionInfo`, and `setCreateTransactionInfo`.
- `OmSnapshotManager.areSnapshotChangesFlushedToDB` and `isSnapshotFlushedToDB`.
- `TransactionInfo`, `TermIndex`, `CacheKey`, and `CacheValue` model table/cache transaction state.

## Control Flow
Setup creates a temporary `OmMetadataManagerImpl`. Table tests assert the snapshot table exists and supports put/get/delete. The SST-filtered test toggles and persists the filtered flag. Transaction tests add snapshot info, manipulate transaction info table and cache entries, and assert flush helper results for null snapshots, null transaction fields, cached snapshot updates, matching term/index, greater index, and greater term/index.

## State and Persistence Behavior
The tests write actual metadata table rows and transaction table rows in a temp OM DB. They also use table cache entries to emulate unflushed in-memory updates. Flush helpers compare snapshot transaction markers against the OM transaction table to decide whether snapshot metadata is durable.

## Dependencies and Integration Points
This test integrates `SnapshotInfo` serialization/table storage with `OmSnapshotManager` flush checks used by snapshot lifecycle services.

## Risks and Edge Cases
- It focuses on transaction comparison semantics, not full snapshot creation/deletion workflows.
- Cache behavior is manually injected, so it assumes table cache semantics remain compatible.

## Test Signals
Passing means snapshot metadata rows persist correctly, SST-filtered state is stored, and transaction flush checks return expected safety decisions.
