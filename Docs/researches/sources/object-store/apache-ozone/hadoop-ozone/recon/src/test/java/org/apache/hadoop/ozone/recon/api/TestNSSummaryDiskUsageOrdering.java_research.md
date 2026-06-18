# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestNSSummaryDiskUsageOrdering.java

## Purpose
Regression test that `NSSummaryEndpoint.getDiskUsage` returns child subpaths sorted by descending size when the caller requests list-file semantics. It uses a synthetic FSO namespace with multiple volumes, buckets, direct files, and directories of deliberately varied sizes.

## Important APIs, types, and functions
- Endpoint under test is `NSSummaryEndpoint.getDiskUsage(path, true, false, true)`.
- Fixture writes use `writeDirToOm` and `writeKeyToOm` against `ReconOMMetadataManager`.
- Reprocessing uses `NSSummaryTaskWithFSO.reprocessWithFSO` to build namespace summary records.
- `verifyOrdering` copies `DUResponse.getDuData`, sorts the copy by `DUResponse.DiskUsage.getSize` descending, and compares subpath order to the endpoint output.
- Temporary OM setup uses `OmMetadataManagerImpl`, `ReconTestInjector`, and a mocked `ReconStorageContainerManagerFacade`.

## Control flow
`setUp` creates an FSO OM metadata manager, injects Recon services, populates the namespace, and reprocesses summaries. `populateOMDB` creates volumes `volA` and `volB`; buckets `bucketA1`, `bucketA2`, `bucketA3`, and `bucketB1`; three directories per bucket; direct files; and one inner file per directory. Tests call `verifyOrdering` for root, volumes, and buckets. The assertion compares only ordering, not exact full size values, because the fixture's size spread is meant to make descending order unambiguous.

## State and persistence behavior
The test persists volume and bucket rows in the OM volume/bucket tables, directory rows in the FSO directory table, key rows in the FSO key table, and computed summaries in Recon namespace summary storage. Bucket `usedBytes` is set to the sum of direct file and directory contents, while each directory total is represented by a child file. There is no real SCM container accounting beyond mocked container and node manager access.

## Dependencies and integration points
This file integrates FSO OM table layout, namespace summary reprocessing, Recon injection, and disk-usage API response ordering. It also depends on positive random object IDs for generated volumes/buckets/directories/files and mocked SCM/node manager availability.

## Risks and edge cases
The test verifies order by subpath equality after sorting a copy; if two siblings have equal sizes, order would be ambiguous, so fixture sizes should remain distinct. It does not validate pagination, recursive size correctness, replica size, or non-FSO layouts. Random object IDs are positive-masked but could still collide in theory, though the probability is negligible.

## Test signals
Signals are ordering assertions for root-level volume children, volume-level bucket children, and bucket-level file/directory children. A failure indicates `getDiskUsage` no longer sorts returned subpaths by descending size when the ordering mode is enabled.
