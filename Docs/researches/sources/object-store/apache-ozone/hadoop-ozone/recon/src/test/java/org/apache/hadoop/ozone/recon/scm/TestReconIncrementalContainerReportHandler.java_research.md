# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconIncrementalContainerReportHandler.java

## Purpose
Tests Recon's incremental container report (ICR) handler. It verifies that datanode replica reports add missing containers, update replica sets, advance container lifecycle state, and merge multiple reports for one datanode.

## Important APIs, types, and functions
- Uses `ReconIncrementalContainerReportHandler.onMessage`.
- Builds `IncrementalContainerReportFromDatanode`, `IncrementalContainerReportProto`, and `ContainerReplicaProto`.
- Integrates `ReconContainerManager`, `NodeManager`/`SCMNodeManager`, `SCMContext`, `EventPublisher`, and helper methods for report creation.

## Control flow
`testProcessICR` creates a missing container report, stubs batch container lookup from the SCM client, registers the datanode in a real `SCMNodeManager`, invokes the handler, and verifies container plus replica state. `testProcessICRStateMismatch` starts with Recon containers in OPEN and feeds CLOSING, QUASI_CLOSED, and CLOSED replica states to verify expected lifecycle advancement without SCM lookup. `testClosingContainerAdvancesViaScmHandlerWithoutScmLookup` starts from CLOSING and advances to QUASI_CLOSED or CLOSED. `testMergeMultipleICRs` merges three single-entry reports and checks report-list growth.

## State and persistence behavior
The handler mutates the real `ReconContainerManager` from the base fixture. Missing containers are fetched in batch from SCM and persisted through the manager. Replica state is stored in container replicas, while lifecycle state is advanced from datanode report state when allowed.

## Dependencies and integration points
This is the bridge from SCM heartbeat event payloads to Recon container state. It depends on node lookup, datanode registration, event handling, container manager add/check logic, and SCM batch lookup for unknown containers.

## Risks and edge cases
The important edge is avoiding SCM lookups for state mismatches that can be resolved locally. Incorrect mappings from replica states to lifecycle states can leave Recon behind SCM or incorrectly downgrade containers. Merged ICR behavior matters for batching multiple heartbeats from the same datanode.

## Test signals
Signals are container existence, one replica recorded, expected lifecycle state, `never()` verification for SCM lookup in local-transition paths, and report-list sizes after merges.
