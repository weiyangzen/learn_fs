# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestNSSummaryTreePrecomputeValues.java

Purpose: JUnit coverage for `NSSummaryTaskWithFSO` materialized namespace totals on a hand-built FILE_SYSTEM_OPTIMIZED tree. It extends `AbstractNSSummaryTaskTest`, overrides OM metadata manager initialization to force custom volume/bucket object IDs, and builds a deterministic tree under `customVol/customBucket1` with nested directories and files.

Important APIs and control flow: `setUp` configures FSO layout, creates `NSSummaryTaskWithFSO`, and calls `populateComplexTree`. Helpers write directories and keys through `OMMetadataManagerTestUtils`, then `runProcessEvents` clears the NSSummary table, runs `reprocessWithFSO`, and applies an `OMUpdateEventBatch` through `processWithFSO`. Tests cover full reprocess totals, file PUT propagation, directory PUT child-dir updates, directory-plus-file PUT ordering, file DELETE propagation, directory DELETE unlinking, and directory-first/file-first deletion ordering.

State and persistence behavior: The tests assert persisted `NSSummary` rows for bucket and directory object IDs, especially `numOfFiles`, `sizeOfFiles`, `childDir`, and `parentId`. Deleting a directory unlinks it by setting parent ID to `0` while ancestor totals are decremented; later file deletion under an already unlinked directory exercises idempotence and exposes nuanced expectations around retained versus zeroed local totals.

Dependencies and integration points: Relies on OM metadata tables, Recon namespace summary manager, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OMDBUpdateEvent`, and `OMUpdateEventBatch`. It validates the contract consumed by Recon namespace APIs and by upgrades that trigger NSSummary rebuilds.

Risks and test signals: Strong signal for aggregate propagation and deletion-order regressions. Risk areas include brittle custom object IDs, event-key simplification to file/dir names rather than full RocksDB keys, and comments/assertions in the directory-first scenario that are not fully aligned, making future changes to deletion semantics easy to misinterpret.
