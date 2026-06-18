# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestClusterStateEndpoint.java

## Purpose
This JUnit test validates `ClusterStateEndpoint.getClusterState`, especially container state counts, SCM/OM service IDs, and storage report DTO typing/fields.

## Important APIs and functions
`setUp` builds a Recon injector with SQL DB, Recon OM, SCM facade, container DB, `ClusterStateEndpoint`, and `ContainerHealthSchemaManager`, then constructs an endpoint with a mocked `OzoneConfiguration`. `testGetContainerCounts` inserts open, deleted, and closed containers and asserts total excludes deleted while open/deleted counts are separate. `testScmAndOmServiceId` verifies config keys flow into `ClusterStateResponse`. `testStorageReportIsClusterStorageReport` uses mocks to validate `ClusterStorageReport` fields from SCM node stats and filesystem usage. `newContainerInfo` and `putContainerInfos` seed containers.

## Control flow, state, and persistence
The primary setup writes Recon SCM container state in the test facade. The storage-report test is pure Mockito and bypasses persistent state. Cluster state aggregation pulls from node manager, pipeline manager, container manager, unhealthy container schema manager, global stats, and configuration.

## Dependencies and integration points
Dependencies include Recon SCM managers, SQL schema manager, `ReconGlobalStatsManager`, `ClusterStateResponse`, `ClusterStorageReport`, SCM node stats, and OM/SCM HA service ID config keys. This endpoint feeds the frontend `overview.tsx` dashboard.

## Risks and edge cases
The total container expectation intentionally excludes `DELETED`; regressions here affect UI dashboard counts. Mocked storage report fields assert specific mapping of capacity, used, remaining, committed, minimum free, reserved, filesystem capacity/used/available. The tests do not cover missing/unavailable global stats or multiple datanodes beyond one mocked node.

## Test signals
Strong contract tests for overview-facing cluster summary fields and storage report type. They help protect frontend assumptions around `openContainers`, `deletedContainers`, `storageReport`, `scmServiceId`, and `omServiceId`.
