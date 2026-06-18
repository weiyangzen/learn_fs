# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconNamespaceSummaryManagerImpl.java

## Purpose
Tests `ReconNamespaceSummaryManagerImpl`, which stores and retrieves namespace summary records used by Recon namespace/file-system summary APIs.

## Important APIs, types, and functions
- Uses `ReconTestInjector` with Recon SQL DB, Recon OM metadata manager, and container DB to obtain `ReconNamespaceSummaryManagerImpl`.
- Exercises `batchStoreNSSummaries`, `commitBatchOperation`, `getNSSummary`, `getNSSummaryTable`, and `clearNSSummaryTable`.
- Uses `RDBBatchOperation` and `NSSummary` fields for file count, file size, bucket distribution, child directories, directory name, and parent id.

## Control flow
Static setup creates the manager and a 40-bucket test array. `@BeforeEach` clears the namespace summary table. `testStoreAndGet` batch-writes three namespace summaries, reads each by object id, checks counts/sizes/names/child dirs, and verifies a missing id returns null. `testInitNSSummaryTable` writes the same data, checks the table is non-empty, clears it, and checks it is empty.

## State and persistence behavior
Namespace summaries are persisted in Recon's container DB as RocksDB records keyed by namespace object id. Batch commit writes multiple summaries atomically. Clearing the table removes all summaries between tests.

## Dependencies and integration points
The manager supports Recon namespace summary tasks and APIs. It depends on Recon DB setup, OM metadata manager fixture, `NSSummary` serialization, and RocksDB batch operations.

## Risks and edge cases
The test covers only three records and table clearing, not updates, parent traversal, bucket histogram correctness beyond round-trip, or concurrent task updates. Static manager reuse requires strict clearing to avoid cross-test contamination.

## Test signals
Signals are exact retrieved file counts, total sizes, directory names, child-dir set size, null for missing id, non-empty table after batch write, and empty table after clear.
