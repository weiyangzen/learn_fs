# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconContainerHealthSummaryEndToEnd.java

## Purpose

This is a comprehensive end-to-end Recon integration test for container state summaries and unhealthy-container summaries. It validates that Recon and SCM agree on lifecycle-state counts after explicit synchronization, and that Recon's `UNHEALTHY_CONTAINERS` Derby records match SCM ReplicationManager classification for induced `UNDER_REPLICATED`, `OVER_REPLICATED`, `MISSING`, and `EMPTY_MISSING` scenarios. It also documents the important boundary where CLOSED empty missing containers are classified as `EMPTY` and intentionally are not persisted as unhealthy records.

## Important APIs, types, and functions

The class drives `MiniOzoneCluster`, `ReconService`, `ReconStorageContainerManagerFacade`, `ReconContainerManager`, `ContainerManager`, `ReplicationManagerReport`, `ContainerHealthSchemaManager`, `ContainerInfo`, `ContainerReplica`, `Pipeline`, `XceiverClientManager`, and `ContainerProtocolCalls`. Test entry points are `testContainerStateSummaryMatchesBetweenSCMAndRecon()`, `testContainerHealthSummaryMatchesBetweenSCMAndRecon()`, and `testComprehensiveSummaryReport()`. Scenario helpers include `setupStateSummaryScenario()`, `setupHealthSummaryScenario()`, `setupUnderReplicatedContainers()`, `setupOverReplicatedContainers()`, `setupMissingContainers()`, `setupEmptyMissingContainers()`, `setupEmptyOnlyContainers()`, `syncAndWaitForReconContainers()`, and `backfillMissingContainersFromScm()`.

## Control flow, state, and persistence

Each test starts a 3-datanode mini cluster with Recon, long full-container-report intervals, delayed background SCM container sync, short missing-container task intervals, and slow SCM replication remediation. The state-summary path allocates containers in SCM, syncs them into Recon, then mutates both SCM and Recon container managers through lifecycle events so counts can be compared state by state. The health-summary path builds targeted container states by creating real containers on pipelines, waiting for replica reports, closing containers in both managers, deleting physical replicas, injecting phantom replicas, mutating `numberOfKeys`, or leaving containers never created on datanodes. It then runs SCM and Recon ReplicationManagers explicitly and queries Recon's unhealthy schema manager.

## Dependencies and integration points

The test integrates Recon SCM sync, SCM container lifecycle state machines, datanode container reports, Recon's in-memory container manager, SCM and Recon ReplicationManager health-check chains, and the Derby-backed unhealthy-container schema. It depends on event queues being drained and on direct manager mutations being visible to later health scans. `LambdaTestUtils.await()` guards asynchronous replica propagation, and custom logging helpers emit report-like summaries.

## Risks and test signals

This file intentionally manipulates internal metadata and physical datanode container files, so race control is the main risk. The long FCR interval prevents removed replicas from being reintroduced; remediation intervals prevent SCM from healing states before assertions; and manual event-queue drains reduce timing windows. The most important behavioral signal is the distinction between `MISSING` and `EMPTY_MISSING`: Recon refines missing empty CLOSING containers into `EMPTY_MISSING`, while CLOSED 0-key/0-replica containers remain `EMPTY` and are not stored in `UNHEALTHY_CONTAINERS`. Failure signals include replica counts not converging, Recon missing synced containers, mismatch between SCM and Recon lifecycle counts, or stale unhealthy rows after recovery.
