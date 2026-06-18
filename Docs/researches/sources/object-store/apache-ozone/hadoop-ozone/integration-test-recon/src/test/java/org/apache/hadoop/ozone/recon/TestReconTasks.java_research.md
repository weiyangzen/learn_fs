# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconTasks.java

## Purpose

This integration test suite exercises Recon's `ContainerHealthTask` and SCM container sync behavior. It covers unhealthy states persisted in `UNHEALTHY_CONTAINERS`: `UNDER_REPLICATED`, `EMPTY_MISSING`, `MISSING`, `OVER_REPLICATED`, `NEGATIVE_SIZE`, and `REPLICA_MISMATCH`, while documenting why `MIS_REPLICATED` and `ALL_REPLICAS_BAD` are not covered here.

## Important APIs, types, and functions

The suite uses `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `ContainerHealthSchemaManager`, SCM `ContainerManager`, `PipelineManager`, `ContainerReplica`, `ContainerChecksums`, `XceiverClientGrpc`, `XceiverClientRatis`, and helper methods from `TestOzoneContainer`. Test methods are `testSyncSCMContainerInfo()`, `testContainerHealthTaskDetectsUnderReplicatedAfterNodeFailure()`, `testContainerHealthTaskDetectsEmptyMissingWhenAllReplicasLost()`, `testContainerHealthTaskDetectsMissingForContainerWithKeys()`, `testContainerHealthTaskDetectsOverReplicatedAndNegativeSize()`, and `testContainerHealthTaskDetectsReplicaMismatch()`.

## Control flow, state, and persistence

Each test starts a three-datanode cluster with short container/pipeline reports, tuned dead-node intervals, and slow SCM remediation. Sync testing allocates and closes SCM containers, verifies Recon is behind, then calls `triggerSCMContainerSync()`. Health tests create real containers, wait for Recon replica reports, directly transition lifecycle state in SCM and Recon when needed, and call `reconScm.getReplicationManager().processAll()` to force scans. Some scenarios use physical datanode shutdown and restart; others inject or remove `ContainerReplica` entries directly in Recon metadata for deterministic missing, over-replicated, negative-size, and checksum-mismatch states.

## Dependencies and integration points

The tests integrate datanode reports, SCM dead-node handling, Recon replica bookkeeping, lifecycle-state-gated health handlers, Recon-specific checks such as negative size and checksum mismatch, and Derby unhealthy-row cleanup after recovery. RF3 paths deliberately use `XceiverClientRatis` so create-container commands reach all three replicas; RF1 paths use `XceiverClientGrpc`.

## Risks and test signals

Main risks are asynchronous replica reports, dead-node timing, and health-handler ordering. The tests wait for expected replica counts before mutating state and repeatedly force health scans during waits. Key signals include unhealthy rows appearing only in the expected state, rows clearing after recovery, `MISSING` being distinct from `EMPTY_MISSING` based on `numberOfKeys`, co-detection of `NEGATIVE_SIZE` with over-replication, and cleanup of `REPLICA_MISMATCH` after checksums become uniform.
