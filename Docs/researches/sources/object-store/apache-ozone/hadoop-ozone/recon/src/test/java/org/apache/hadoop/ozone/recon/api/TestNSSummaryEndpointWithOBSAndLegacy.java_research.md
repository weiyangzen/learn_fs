# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithOBSAndLegacy.java

## Purpose
Tests `NSSummaryEndpoint` against Object Store buckets and Legacy buckets when filesystem paths are disabled. The fixture models two volumes, four buckets, and nine flat keys, then verifies namespace basic info, disk usage, replicated disk usage, quota usage, file-size distribution, and utility path behavior.

## Important APIs, Types, And Functions
Primary APIs under test are `NSSummaryEndpoint.getBasicInfo`, `getDiskUsage`, `getQuotaUsage`, and `getFileSizeDistribution`. The test also covers `EntityHandler.parseRequestPath`, `BucketHandler.getKeyName`, `BucketHandler.buildSubpath`, `OmUtils.normalizePathUptoBucket`, and `ReconUtils.constructFullPath`. It uses `ReconTestInjector`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, `NSSummaryTaskWithOBS`, `NSSummaryTaskWithLegacy`, `OMMetadataManager`, `OmVolumeArgs`, `OmBucketInfo`, `OmKeyInfo`, `OmKeyLocationInfoGroup`, `DUResponse`, `NamespaceSummaryResponse`, `QuotaUsageResponse`, and `FileSizeDistributionResponse`.

## Control Flow
`setUp` creates an OM metadata database with `OZONE_OM_ENABLE_FILESYSTEM_PATHS=false`, injects a mocked Recon SCM, populates OM volume, bucket, and key tables, then reprocesses namespace summaries with both OBS and Legacy tasks. The test cases call endpoint methods at root, volume, bucket, and key paths and compare response types, counts, object metadata, sizes, status codes, and distributions. Additional helper paths insert multi-block keys and mock container replica counts so replicated-size calculations can be validated independently from logical file sizes.

## State And Persistence
State lives in temporary RocksDB-backed OM metadata tables and Recon namespace summary tables created under JUnit `@TempDir`. `populateOMDB` writes volumes, buckets, and flat keys with fixed object IDs, quotas, sizes, and bucket layouts. Multi-block helpers overwrite key table entries with block location groups and depend on a mocked `ContainerManager` returning replica sets for containers 1 through 6. No external cluster state is used.

## Dependencies And Integration Points
This test integrates Recon REST endpoint code with OM metadata table semantics, namespace summary reprocessing tasks, SCM node/container replica lookup, quota utilities, and path normalization helpers. It specifically exercises the boundary where Legacy buckets behave like OBS buckets because filesystem paths are disabled.

## Risks
The assertions rely on hard-coded object IDs, path strings, and sorted response order for disk usage child entries. Replicated-size tests depend on mocked replica counts matching the constants, so changes in `QuotaUtil`, container-replica interpretation, or namespace summary aggregation can break many expectations. The flat-key behavior is sensitive to path normalization around leading, trailing, and repeated slashes.

## Test Signals
Strong signals include root counts of 2 volumes, 4 buckets, and 9 keys; bucket layout reporting for OBS versus Legacy; `PATH_NOT_FOUND` for invalid paths; `TYPE_NOT_APPLICABLE` for key quota usage; per-bin file-size distribution checks; and replicated-size totals for root, volume, bucket, and key paths.
