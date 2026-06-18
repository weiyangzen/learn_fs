# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryEndpointWithFSO.java

## Purpose
Comprehensive REST-level test for `NSSummaryEndpoint` over `FILE_SYSTEM_OPTIMIZED` buckets. It constructs a three-volume namespace with nested directories, files, quotas, file-size bins, standalone-replicated keys, Ratis factor-three keys, and multi-block keys, then validates basic info, disk usage, replicated size, quota usage, file-size distribution, and full-path reconstruction.

## Important APIs, types, and functions
- Endpoint APIs under test include `getBasicInfo`, `getDiskUsage`, `getQuotaUsage`, and `getFileSizeDistribution` through direct endpoint calls and shared `NSSummaryTests` helper assertions.
- FSO fixture writes use `writeDirToOm` and `writeKeyToOm` with parent object IDs, bucket object IDs, volume object IDs, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and optional replication configs/location groups.
- `NSSummaryTaskWithFSO.reprocessWithFSO` converts OM tables into Recon namespace summaries.
- Replication fixtures use `OmKeyLocationInfoGroup`, `BlockID`, `ContainerReplica`, mocked `ContainerManager.getContainerReplicas`, `StandaloneReplicationConfig`, `RatisReplicationConfig`, and `QuotaUtil.getReplicatedSize`.
- `ReconUtils.constructFullPath` is tested for normal FSO parent traversal and for negative parent IDs that signal rebuild-in-progress.

## Control flow
`setUp` creates an FSO OM metadata manager, binds `NSSummaryEndpoint` with a mocked Recon SCM, populates a base namespace, adds `vol3` with Ratis factor-three keys, overwrites selected keys with multi-block location info, and runs FSO summary reprocessing. Basic-info tests delegate common expectations to `NSSummaryTests`. Disk-usage tests cover root, volume, bucket, directory, key, invalid path, and replica-aware modes. Quota and file-size distribution tests assert expected aggregate values. Path-construction tests build `OmKeyInfo` instances with parent IDs and verify reconstructed paths, including an explicit corrupt/rebuilding summary with parent id `-1`.

## State and persistence behavior
The file persists volumes, buckets, directories, and keys into temporary OM RocksDB tables and persists derived namespace summaries in Recon summary storage. FSO parent-child structure is represented by object IDs, so directory and file parent IDs are central to path lookup and summary propagation. Replica-aware size depends on mocked SCM container replica sets for six container IDs: some under-replicated, some over-replicated, and some with five replicas, plus Ratis factor-three keys under `vol3`. The mocked SCM node manager reports root quota stats used by quota calculations.

## Dependencies and integration points
This test bridges OM FSO key/directory layout, Recon namespace summary task output, `NSSummaryEndpoint` path parsing and entity handlers, quota utilities, SCM container replica lookup, Recon node stats, and shared `NSSummaryTests` contracts. It verifies that endpoint behavior remains layout-aware while exposing the same REST semantics as legacy buckets.

## Risks and edge cases
There is substantial duplicated constant arithmetic; any fixture change must update raw size, replica size, quota, and file-size-bin expectations consistently. The test relies on ordering of `duData().get(0)` for some replica assertions, so sorting changes can break it. Mocked container replica counts may not cover EC or closed-container behavior. The negative-parent tests are important because FSO path reconstruction can otherwise return misleading partial paths while summaries are being rebuilt.

## Test signals
Signals include shared basic-info expectations, exact root/volume/bucket/dir/key DU counts and sizes, `PATH_NOT_FOUND` and `TYPE_NOT_APPLICABLE` statuses, propagated `sizeWithReplica` at every hierarchy level, Ratis factor-three replicated-size checks, quota values and usage, file-size distribution bins, and full-path strings for nested FSO files.
