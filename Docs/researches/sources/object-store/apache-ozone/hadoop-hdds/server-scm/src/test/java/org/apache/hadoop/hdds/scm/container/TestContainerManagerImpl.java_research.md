# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerManagerImpl.java

## Purpose

This test class verifies `ContainerManagerImpl` allocation, matching, lifecycle transitions, listing/counting, EC support, and pending replica operation completion. It uses a real SCM DB store and mock pipeline manager to cover persistent container table behavior.

## Important APIs, Types, and Functions

- `ContainerManagerImpl.allocateContainer`, `getMatchingContainer`, `getContainer`, `getContainers`, `getContainerStateCount`, `updateContainerState`, `transitionDeletingOrDeletedToTargetState`, `updateContainerReplica`, and `removeContainerReplica`.
- `DBStoreBuilder` and `SCMDBDefinition.CONTAINERS` provide the real container table.
- `SequenceIdGenerator` assigns container IDs.
- `MockPipelineManager` and spied `PipelineManager.checkSpaceAndRecordAllocation` control allocation viability.
- `ContainerReplicaPendingOps.completeAddReplica` and `completeDeleteReplica` are verified.

## Control Flow and State Behavior

`setUp` creates an SCM DB in a temp directory, HA stub, mock node manager, sequence ID generator, spied mock pipeline manager, one RATIS pipeline, and `ContainerManagerImpl`. Allocation tests verify an initially empty manager gains retrievable containers. Matching-container tests force space-check failure to return null and success to allocate for both RATIS and EC pipelines. Lifecycle tests traverse OPEN to CLOSING, QUASI_CLOSED, CLOSED, then DELETING/DELETED back to CLOSED through `transitionDeletingOrDeletedToTargetState`, while negative tests reject OPEN-to-CLOSED repair transitions. Listing tests allocate ten containers, page by start ID and count, filter by lifecycle state, and assert state counts after transitions. Replica tests verify updating/removing replicas completes pending add/delete operations.

## State and Persistence

The container table and sequence table are real DB tables under `@TempDir`; they are closed after each test. Container lifecycle state is persisted through `ContainerManagerImpl` into the table. Pending operation state is mocked and verified through method calls.

## Dependencies and Integration Points

Dependencies include SCM DB definitions, HA manager stubs, node manager mock, pipeline manager, replication configs, `ContainerStateMap`, `ContainerReplicaPendingOps`, and Ozone lifecycle events. The test is a central integration point for container metadata and pipeline space accounting.

## Risks and Test Signals

Risk areas include allocating containers when datanodes lack space, illegal lifecycle repairs, incorrect pagination/state indexes, EC/RATIS divergence, and pending operation leaks. Signals are strong because tests use real DB tables and assert exact state counts, null/non-null allocation outcomes, and pending-op method invocations.
