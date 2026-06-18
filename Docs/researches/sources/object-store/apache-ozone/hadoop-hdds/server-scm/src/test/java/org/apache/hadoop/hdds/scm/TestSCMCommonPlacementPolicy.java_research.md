# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestSCMCommonPlacementPolicy.java

## Purpose

This JUnit 5 test class exercises `SCMCommonPlacementPolicy`, the shared SCM placement-policy base used for datanode selection and container placement validation. It focuses on rack-aware mis-replication repair, over-replication removal, node validity under committed-space accounting, and placement validation when topology information is incomplete or stale.

## Important APIs, Types, and Functions

- `DummyPlacementPolicy extends SCMCommonPlacementPolicy` supplies deterministic rack mapping through `getPlacementGroup`, `getRequiredRackCount`, and `chooseNode`.
- `testReplicasToFixMisreplication(...)` wraps `replicasToCopyToFixMisreplication` and verifies copy counts per rack.
- `replicasToRemoveToFixOverreplication` is tested across indexed and non-indexed replicas.
- `isValidNode` is tested with mocked `DatanodeInfo`, `NodeStatus`, storage reports, metadata reports, `committed`, and `freeSpaceToSpare`.
- `validateContainerPlacement` is tested with dead/in-maintenance nodes and a topology that temporarily reports zero racks.

## Control Flow and State Behavior

`setup` creates a `MockNodeManager` with ten synthetic nodes and a temporary SCM configuration. Most tests build a `DummyPlacementPolicy`, map datanode indices to mock rack `Node` instances, synthesize `ContainerReplica` sets using `HddsTestUtils`, and assert which replicas should be copied or removed. The mis-replication path groups replicas by placement group and expects extra replicas from overfull racks to be selected for copying. The over-replication path verifies that duplicates or rack-skewed replicas are preferred for removal.

The storage-space test drives `isValidNode` through sequential storage report returns, proving that increasing committed bytes can make an otherwise writable node invalid when `remaining - committed` no longer exceeds the larger of requested space and spare-space reservation. Placement-validation tests mock `NodeManager` and `NetworkTopology` state to ensure maintenance nodes can use their embedded network location and zero-rack topology does not trigger divide-by-zero.

## State and Persistence

The class has no durable persistence. State is in-memory test fixtures: rack maps, mock topology, mock node status, synthetic storage reports, and replica sets. It indirectly validates production behavior that depends on SCM topology and datanode storage-report state.

## Dependencies and Integration Points

The tests integrate with `NodeManager`, `NetworkTopology`, `DatanodeInfo`, `NodeStatus`, `ContainerReplica`, `ContainerID`, `SCMException`, `HddsTestUtils`, `MockNodeManager`, and Mockito. They are regression coverage for replication manager decisions that call common placement utilities.

## Risks and Test Signals

Risk areas are rack-count arithmetic, choosing copy/removal candidates when replica indices are absent, honoring uncopyable replicas, accounting for committed bytes, and handling transient topology loss. Strong test signals include explicit per-rack expected copy counts, exact over-replication removal sets, and HDDS-15350 zero-rack regression coverage.
