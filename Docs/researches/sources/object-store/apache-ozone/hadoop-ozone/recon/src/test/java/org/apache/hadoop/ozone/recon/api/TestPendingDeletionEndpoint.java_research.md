# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestPendingDeletionEndpoint.java

## Purpose
Unit-tests `PendingDeletionEndpoint` dispatch and response behavior for component-specific pending deletion metrics: datanode (`dn`), SCM (`scm`), and OM (`om`).

## Important APIs, Types, And Functions
The key method is `PendingDeletionEndpoint.getPendingDeletionByComponent`. Collaborators are `ReconGlobalMetricsService`, `DataNodeMetricsService`, `StorageContainerLocationProtocol`, `DataNodeMetricsServiceResponse`, `DatanodePendingDeletionMetrics`, `ScmPendingDeletion`, and `HddsProtos.DeletedBlocksTransactionSummary`.

## Control Flow
`setup` builds the endpoint with Mockito mocks. Validation tests send missing, empty, invalid, and whitespace components plus invalid datanode limits. Datanode tests return finished or in-progress `DataNodeMetricsServiceResponse` objects and assert OK versus accepted responses. SCM tests return a deleted-block summary, null, or an exception. OM tests pass through the pending-size map calculated by `ReconGlobalMetricsService`.

## State And Persistence
No persistent state is created. All state is mock return data: datanode pending deletion lists, SCM summary values, and OM pending size maps.

## Dependencies And Integration Points
The endpoint integrates Recon global metrics, datanode metrics collection, and SCM protocol deleted-block summaries behind one REST parameter. The test ensures component names are case-normalized for valid `DN` input but otherwise strictly validated.

## Risks
The whitespace component case currently returns the invalid-component message rather than the missing-component message. SCM exception handling intentionally returns OK with `-1` sentinel values, which clients must distinguish from real metrics. Limit validation only applies to datanode collection.

## Test Signals
Signals include 400 for missing or invalid components, 400 for `dn` limit below 1, 200 for finished datanode and OM metrics, 202 for in-progress datanode metrics, 204 when SCM summary is absent, and sentinel `-1` values when SCM summary retrieval fails.
