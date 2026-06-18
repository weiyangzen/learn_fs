# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManagerFSO.java

## Purpose

This integration test validates Recon namespace summary behavior when OM uses FILE_SYSTEM_OPTIMIZED bucket layout by default. It creates volume/bucket/key hierarchies through the client API, syncs Recon from OM, and queries `NSSummaryEndpoint` for directory and root summary responses.

## Important APIs, types, and functions

The class uses `MiniOzoneCluster`, `ReconService`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `TestDataUtil.createKey()`, `OzoneManagerServiceProviderImpl`, `ReconNamespaceSummaryManager`, `ReconOMMetadataManager`, `NSSummaryEndpoint`, and `NamespaceSummaryResponse`. The main test is `testNamespaceSummaryAPI()`, supported by `writeKeys()`, `addKeys()`, and `waitForAsyncProcessingToComplete()`.

## Control flow, state, and persistence

Setup sets the default bucket layout to FSO, starts a three-datanode cluster, waits for RF1 pipelines, and initializes an object store. The test creates ten volumes and buckets with keys under `dirN/keyN`, syncs OM data into Recon, waits for async processing, and checks that `/vol1/bucket1/dir1` is a directory with one key and no child directories. It then creates two more entries, syncs again, checks Recon's volume table via `getSkipCache()`, and validates root counts for volume, bucket, directory, and key totals.

## Dependencies and integration points

The test integrates client-side key creation, FSO OM metadata, Recon OM sync, Recon namespace summary indexing, and the namespace summary REST resource instantiated directly in-process.

## Risks and test signals

The async wait helper is time-based and may race under slow event processing. The expected root volume count is 13 while only 12 loop-created volumes exist, implying a built-in/system/default volume is counted and should be documented if that behavior changes. The comments note expectation changes after removing deleted-table processing. Positive signals are directory entity typing, count stats for a specific directory, Recon OM volume-table visibility after sync, and expected root aggregate counts.
