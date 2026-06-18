# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/DatanodeDeletedBlockTransactions.java

Purpose: In-memory wrapper holding deleted-block transactions selected for each datanode during a scan.

Important APIs and types: Maintains `Map<DatanodeID, List<DeletedBlocksTransaction>>` and `blocksDeleted`. Methods add transactions, expose the map, count blocks, list transaction IDs, count blocks per datanode, and check emptiness.

Control flow: `DeletedBlockLogImpl` fills this object while scanning; `SCMBlockDeletingService` converts each datanode entry into a `DeleteBlocksCommand`.

State and persistence behavior: Scan-local in-memory state only. `blocksDeleted` counts replica work, not unique blocks.

Dependencies and integration points: Bridges log scanning and command creation; also supports per-datanode throttling.

Risks: Not synchronized and intended for single-threaded scan use. Replica-counted block totals can be mistaken for unique block totals.

Test signals: Verify per-datanode accumulation, block counts, empty state, and transaction ID list formatting.
