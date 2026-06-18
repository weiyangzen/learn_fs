# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManager.java

## Purpose
`TestContainerStateManager` validates core `ContainerStateManagerImpl` behavior around replica tracking, lifecycle transitions, persistence reload, sequence-id handling, and stale-replica delete commands. It complements the report-handler tests by directly asserting state-manager APIs and by routing selected report-handler calls through a real state manager.

## Important APIs, Types, and Functions
The test fixture creates a `ContainerStateManagerImpl` with a real SCM DB table, mocked `PipelineManager`, `MockNodeManager`, mocked `ContainerManager`, `SCMContext`, and mocked `EventPublisher`. Important methods under test include `addContainer`, `getContainerReplicas`, `transitionDeletingOrDeletedToTargetState`, `getContainerIDs`, `reinitialize`, and `updateContainerStateWithSequenceId`. Helper methods `allocateContainer`, `addReplica`, `sendReportAndCaptureDeleteCommand`, `verifyForceDeleteCommand`, `verifyContainerState`, and `getContainerReportsProto` keep the scenarios focused.

## Control Flow and State Behavior
The first tests verify that adding two or three `ContainerReplica` entries produces the expected replica count independent of the replication factor. `testTransitionDeletingOrDeletedToTargetState` builds raw `ContainerInfoProto` records in DELETING or DELETED and asserts they can transition to CLOSED through the special transition API. The negative parameterized test confirms the same API rejects other lifecycle states such as CLOSING, QUASI_CLOSED, CLOSED, and RECOVERING by surfacing `InvalidContainerStateException`.

Stale replica tests use `ContainerReportHandler` with the mocked `ContainerManager` delegation to simulate deleted-container report handling. For DELETED RATIS containers, CLOSED replicas with equal or lower BCSID receive `DeleteContainerCommand` with `force=true`, and the container remains DELETED. For DELETING or DELETED EC containers, non-empty stale replicas are also force-deleted without changing the SCM lifecycle state.

Persistence-sensitive coverage includes `testGetContainerIDs`, which filters stored containers by lifecycle state, and `testReinitializeWithOpenContainerWithoutPipelineID`, which directly inserts an OPEN container with no pipeline ID into the SCM table and verifies `reinitialize` does not call `addContainerToPipelineSCMStart` with a null pipeline. `testSequenceIdOnStateUpdate` ensures newer sequence IDs advance state metadata while older sequence IDs are ignored after a later transition.

## Dependencies and Integration Points
This file depends on SCM DB definitions, HA stubs, protobuf lifecycle enums, pipeline IDs, replication configs, `DeleteContainerCommand`, and `SCMEvents.DATANODE_COMMAND`. It is an integration point between state-manager lifecycle validation and container report delete-command emission.

## Risks and Test Signals
The suite targets high-risk metadata corruption paths: illegal resurrection transitions, stale replica cleanup, missing pipeline IDs during SCM restart, and sequence-id regression. Signals include state assertions, captured command assertions, exception type checks, and Mockito verification of pipeline-manager calls. The tests use mocked managers for surrounding SCM services, so they validate state-manager semantics rather than full cluster behavior.
