<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PendingDeletionEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PendingDeletionEndpoint.java

## Purpose

`PendingDeletionEndpoint` provides admin-only pending-deletion metrics across datanodes, SCM, and OM via `/pendingDeletion`.

## Important APIs and Types

The single public method `getPendingDeletionByComponent(component, limit)` dispatches `component=dn`, `scm`, or `om`. DN responses come from `DataNodeMetricsServiceResponse`; SCM responses use `ScmPendingDeletion`; OM responses are a map from `ReconGlobalMetricsService.calculatePendingSizes`.

## Control Flow

The endpoint validates `component`, normalizes it, and switches by value. DN requests reject `limit < 1`, return HTTP 200 when metric collection is finished, and HTTP 202 while collection is still pending/running. SCM requests call `scmClient.getDeletedBlockSummary`, map total block size, replicated size, and count, return 204 for null summary, and return `-1` sentinel values on exception. OM requests compute pending key and directory sizes from Recon global/namespace state.

## State and Persistence

No endpoint-local state exists. DN metrics may reflect state collected asynchronously by `DataNodeMetricsService`; SCM metrics come from live SCM protocol; OM metrics come from Recon persisted tables.

## Dependencies and Integration Points

It integrates with `ReconGlobalMetricsService`, `DataNodeMetricsService`, and `StorageContainerLocationProtocol`.

## Risks and Edge Cases

SCM failures are hidden behind HTTP 200 with `-1` fields, while DN invalid limits use HTTP 400 and in-progress states use HTTP 202. Clients must understand this mixed error model. A null SCM summary becomes 204 with no entity.

## Test Signals

Tests should cover required component validation, component aliases/case normalization, DN limit validation and status mapping, SCM success/null/failure behavior, and OM pending-size calculation failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PendingDeletionEndpoint.java -->
