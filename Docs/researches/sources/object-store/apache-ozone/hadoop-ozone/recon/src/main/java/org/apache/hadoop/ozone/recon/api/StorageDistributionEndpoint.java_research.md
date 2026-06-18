<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/StorageDistributionEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/StorageDistributionEndpoint.java

## Purpose

`StorageDistributionEndpoint` provides admin-only cluster storage distribution and a CSV download combining datanode capacity with pending-deletion metrics.

## Important APIs and Types

`getStorageDistribution` returns `StorageCapacityDistributionResponse` with `DatanodeStorageReport`, `GlobalStorageReport`, `GlobalNamespaceReport`, and `UsedSpaceBreakDown`. `/download` returns either metric-collection status or a CSV built from `DatanodePendingDeletionMetrics` joined with current datanode storage reports.

## Control Flow

The main GET collects datanode reports, sums them into global storage, obtains open-key/MPU bytes, calculates namespace metrics from pending OM sizes, finalized replicated DU at root, and key counts, then builds the response. Download first asks `DataNodeMetricsService` for collected metrics; if unfinished it returns HTTP 202 JSON, otherwise it joins metrics by datanode UUID, builds CSV headers and column extractors, derives a UTC filename from cluster id and timestamp, and delegates to `ReconUtils.downloadCsv`.

## State and Persistence

The endpoint has no mutable state. It reads live Recon node-manager state, Recon global stats, namespace summaries through `NSSummaryEndpoint`, DataNodeMetricsService collected state, and Recon context cluster id.

## Dependencies and Integration Points

It integrates with SCM node stats, `ReconGlobalMetricsService`, `ReconGlobalStatsManager`, `NSSummaryEndpoint`, `DataNodeMetricsService`, and CSV download utilities.

## Risks and Edge Cases

`calculateNamespaceMetrics` stores pending sizes in local variables but does not put them back into the returned map, so fallback code mentioning those keys is not reflected in the response builder. Finalized bytes are computed by invoking another endpoint method and casting the entity to `DUResponse`; changes to that endpoint can break storage distribution. Download maps metrics to views even when the storage report is missing, using `-1` fields. Main response catches broad exceptions and returns HTTP 500 text.

## Test Signals

Tests should cover aggregation consistency from one datanode snapshot, missing node stats, root DU failure, missing global stats, pending-size failure, CSV unfinished/finished/missing-data paths, cluster-id fallback, and CSV column values for missing reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/StorageDistributionEndpoint.java -->
