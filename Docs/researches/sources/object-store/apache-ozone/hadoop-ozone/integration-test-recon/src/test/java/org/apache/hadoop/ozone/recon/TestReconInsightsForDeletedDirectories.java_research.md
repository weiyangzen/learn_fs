# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconInsightsForDeletedDirectories.java

## Purpose

This integration test validates Recon OM DB insight reporting for deleted directories in FILE_SYSTEM_OPTIMIZED buckets. It exercises simple, nested, and wide directory deletions under both RATIS THREE and EC RS-3-2 replication, then verifies Recon's deleted-directory insight sizes and namespace summary accounting.

## Important APIs, types, and functions

The test uses `MiniOzoneCluster`, Hadoop `FileSystem`, `OzoneClient`, `OzoneBucket`, OM `Table` instances for file, directory, and deleted-directory tables, `ReconOMMetadataManager`, `ReconNamespaceSummaryManagerImpl`, `ReconGlobalMetricsService`, and `OMDBInsightEndpoint`. Parameterization comes from `replicationConfigs()`. Main tests are `testGetDeletedDirectoryInfo()`, `testGetDeletedDirectoryInfoForNestedDirectories()`, and `testGetDeletedDirectoryInfoWithMultipleSubdirectories()`. Helpers include `createLargeDirectory()`, `cleanupTables()`, `removeAllFromDB()`, `assertTableRowCount()`, `syncDataFromOM()`, and `waitForAsyncProcessingToComplete()`.

## Control flow, state, and persistence

The cluster disables frequent directory and block deletion services, enables ACLs, and sets a small FSO iterate batch size. Each test creates an FSO bucket with a default replication config, creates directory trees through the Hadoop FS API, checks OM table row counts, syncs OM data into Recon, and then checks Recon table row counts. After deletion, the tests instantiate `OMDBInsightEndpoint` directly and assert `KeyInsightInfoResponse` unreplicated and replicated sizes. Cleanup manually deletes rows from OM deleted-directory, file, and directory tables.

## Dependencies and integration points

The tests integrate the Ozone FS client, OM metadata tables, Recon OM snapshot synchronization, Recon namespace summary updates, quota replicated-size calculations, and the OM DB insight endpoint. `QuotaUtil.getReplicatedSize()` is used as the replication-aware expected value, making the same assertions valid for RATIS and EC.

## Risks and test signals

The async wait helper is time-based rather than tied to the Recon event buffer, so slow CI environments can still race namespace-summary processing. Manual table cleanup touches OM metadata directly and assumes no other test state is sharing the cluster. Strong test signals are row-count convergence in OM and Recon tables, deleted-directory table growth after delete, and insight endpoint sizes of 10, 3, and 100 bytes/files adjusted by replication.
