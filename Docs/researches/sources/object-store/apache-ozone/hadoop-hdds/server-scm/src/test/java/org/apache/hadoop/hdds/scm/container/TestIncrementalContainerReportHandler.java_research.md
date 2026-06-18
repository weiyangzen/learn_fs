# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestIncrementalContainerReportHandler.java

## Purpose
`TestIncrementalContainerReportHandler` tests the incremental-report counterpart to the full container report suite. It verifies that single-container deltas update SCM replica state, lifecycle state, node membership, and checksum metadata consistently, and that incremental and full reports do not race into inconsistent `NodeManager` and `ContainerStateManager` views.

## Important APIs, Types, and Functions
The central type is `IncrementalContainerReportHandler`, driven by `IncrementalContainerReportFromDatanode` and `IncrementalContainerReportProto`. The fixture uses a real `SCMNodeManager`, `NetworkTopologyImpl`, `EventQueue`, `SCMStorageConfig`, mocked `HDDSLayoutVersionManager`, `MockPipelineManager`, real `ContainerStateManagerImpl`, and mocked `ContainerManager`. Helpers include `getIncrementalContainerReportProto`, `setupECContainerForTesting`, `createAndHandleICR`, and `testReplicaIndexUpdate`. The file imports checksum helpers and full-report proto helpers from `TestContainerReportHandler`.

## Control Flow and State Behavior
The report handler is called through `reportHandler.onMessage(icrFromDatanode, publisher)`. Tests cover CLOSING to CLOSED, CLOSING to QUASI_CLOSED, and QUASI_CLOSED to CLOSED transitions for RATIS containers, plus EC-specific close eligibility based on replica indexes. A lower BCSID CLOSED report is deliberately sent against CLOSING and QUASI_CLOSED containers to assert the handler does not throw and leaves state unchanged. `testOpenWithUnhealthyReplica` verifies an UNHEALTHY incremental report for an OPEN container moves the SCM container to CLOSING.

Replica and node state mutation is covered by `testDeleteContainer`: a DELETED replica report removes one replica from the container-state manager and removes the container from the reporting datanode in `NodeManager`, while preserving other datanode memberships. `testICRFCRRace` runs full and incremental handlers concurrently using a two-thread executor for ten iterations; it asserts a container is present in both `NodeManager` and replica state, or in neither, preventing the HDDS-5249 split-brain condition.

Checksum tests mirror the full-report suite for incremental reports: absent `dataChecksum` leaves stored replica checksums zero, unique checksum reports update each replica independently, and later matching checksums converge all replica records. EC replica-index validation prevents invalid index 0 or out-of-range index 6 from replacing stored indexes and accepts valid index changes.

## Dependencies and Integration Points
This suite integrates with `SCMNodeManager` rather than `MockNodeManager`, giving stronger coverage for node registration and membership mutations. It also uses the SCM metadata DB, HA stub, pipeline manager, layout version manager, and event publisher. It shares lifecycle and checksum semantics with `ContainerReportHandler`, making it a regression guard for parity between FCR and ICR paths.

## Risks and Test Signals
Major risks are missed replica removals, inconsistent node/container state under report races, handler crashes on stale BCSIDs, EC index corruption, and checksum drift. Signals include direct lifecycle assertions, replica count assertions, node-container membership checks, concurrent consistency checks, and checksum equality over every replica.
