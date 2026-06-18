# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestStorageDistributionEndpoint.java

## Purpose
Tests `StorageDistributionEndpoint` cluster storage distribution and CSV download behavior, including datanode filesystem/Ozone capacity aggregation, namespace usage breakdown, pending deletion metrics, in-progress responses, and missing-metrics failures.

## Important APIs, Types, And Functions
The tested methods are `getStorageDistribution` and `downloadDataNodeStorageDistribution`. Important types are `StorageCapacityDistributionResponse`, `DatanodeStorageReport`, `DataNodeMetricsServiceResponse`, `DatanodePendingDeletionMetrics`, `ReconGlobalMetricsService`, `ReconGlobalStatsManager`, `NSSummaryEndpoint`, `ReconNodeManager`, `SCMNodeMetric`, `SpaceUsageSource.Fixed`, and `DUResponse`.

## Control Flow
`setup` constructs the endpoint with mocked SCM, node manager, global metrics, global stats, namespace summary endpoint, datanode metrics service, and Recon context. `mockStorageDistributionData` creates a configurable number of datanodes, storage stats, pending deletion rows, global pending/open MPU summaries, root disk usage with replicas, and global key counts. Tests then assert the JSON endpoint response, accepted download response when collection is in progress, server error when metrics are missing after a finished status, and streamed CSV content plus attachment filename.

## State And Persistence
There is no durable persistence. The endpoint response is driven by mocked datanode lists, per-node SCM stats, filesystem usage, global metrics maps, namespace root DU response, and global stats rows. CSV output is emitted through a `StreamingOutput` entity and captured into memory.

## Dependencies And Integration Points
The endpoint combines SCM node telemetry, filesystem usage, Recon namespace summary disk usage, global stats counts, pending OM deletion sizes, open key summaries, MPU summaries, datanode pending deletion metrics, and Recon cluster ID for export filenames.

## Risks
The endpoint depends on multiple independent services returning internally consistent metrics. The test highlights a finished-but-empty datanode metrics response as an internal server error. Computed Ozone capacity, used, and remaining values subtract reserved, non-Ozone used, and minimum free space, so changes in those formulas will alter both per-node and global assertions.

## Test Signals
Signals include total Ozone used/free/capacity and committed space multiplied by datanode count, namespace total used from pending plus open plus finalized bytes, expected total key count of 14, exact open-key breakdown values, per-node storage reports, accepted JSON for in-progress collection, text error for missing metrics, and CSV rows containing all expected datanode values.
