<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ReconGlobalMetricsService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ReconGlobalMetricsService.java

## Purpose

`ReconGlobalMetricsService` centralizes global OM-derived storage counters used by key insight, pending deletion, and storage distribution APIs.

## Important APIs and Types

It exposes `getOpenKeySummary`, `getDeletedKeySummary`, `getMPUKeySummary`, `getPendingForDeletionDirInfo`, and `calculatePendingSizes`. It reads `GlobalStatsValue` records named by `OmTableInsightTask`, deleted directory entries from `ReconOMMetadataManager.getDeletedDirTable`, and `NSSummary` rows for directory sizes.

## Control Flow

Summary methods fetch global stats keys for count, replicated size, and unreplicated size and return zeroes on `IOException`. Deleted-directory listing optionally seeks to `prevKey`, skips it once, iterates until `limit`, converts each `OmKeyInfo` into `KeyEntityInfo`, accumulates replicated/unreplicated totals using namespace summary sizes, and records `lastKey`. `calculatePendingSizes` combines replicated pending directory size with deleted-key replicated size and uses `-1` sentinels if either side fails.

## State and Persistence

The service is a singleton but holds no mutable state. It reads persisted Recon global stats, OM deleted-dir table, and namespace summary tables.

## Dependencies and Integration Points

It integrates with `ReconGlobalStatsManager`, `ReconOMMetadataManager`, `ReconNamespaceSummaryManager`, `OmTableInsightTask`, and key insight DTOs. `OMDBInsightEndpoint`, `PendingDeletionEndpoint`, and `StorageDistributionEndpoint` use it.

## Risks and Edge Cases

Global stats can be stale relative to OM table scans. Deleted-dir pagination requires `prevKey` to exist exactly or returns an empty response. `getMPUKeySummary` uses key name `totalDataSize` rather than `totalUnreplicatedDataSize`, so clients must account for the naming difference. Directory size lookup returns zero if NSSummary is missing.

## Test Signals

Tests should cover missing global stats, IOException fallback, deleted-dir table null, prevKey exact and missing behavior, limit handling including `-1`, namespace summary missing rows, and `calculatePendingSizes` sentinel behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ReconGlobalMetricsService.java -->
