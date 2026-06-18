<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NSSummaryEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NSSummaryEndpoint.java

## Purpose

`NSSummaryEndpoint` exposes admin-only namespace summary APIs under `/namespace` for entity summaries, disk usage, quota usage, and file-size distribution.

## Important APIs and Types

The main APIs are `/summary`, `/usage`, `/quota`, and `/dist`. Responses use `NamespaceSummaryResponse`, `DUResponse`, `QuotaUsageResponse`, and `FileSizeDistributionResponse`. The endpoint delegates all path-specific work to `EntityHandler.getEntityHandler`.

## Control Flow

Each operation rejects missing or empty `path` with HTTP 400. If Recon OM metadata initialization is incomplete, it returns an initializing response rather than querying tables. Otherwise it constructs an `EntityHandler` from the namespace summary manager, OM metadata manager, SCM, and path, then calls the matching handler method.

## State and Persistence

The endpoint holds injected managers only. Data comes from Recon's OM metadata snapshot tables and namespace summary store; no endpoint-local state is written.

## Dependencies and Integration Points

It is the primary REST entry point for the handler hierarchy in `api.handlers`, and uses `ReconUtils.isInitializationComplete` as a readiness gate. `StorageDistributionEndpoint` also calls `getDiskUsage("/", false, true, false)` to compute finalized replicated bytes.

## Risks and Edge Cases

The APIs return HTTP 200 for path-not-found or initializing states when represented in the body, while only malformed empty paths return HTTP 400. Handler behavior differs sharply by bucket layout. Recursive aggregation relies on namespace summary materialization being current with OM DB.

## Test Signals

Tests should cover root, volume, bucket, directory, key, unknown path, initializing state, layout-specific paths, `files`, `replica`, and `sortSubPaths` options, quota type-not-applicable responses, and stale/missing NSSummary rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NSSummaryEndpoint.java -->
