# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/SimpleMockNodeManager.java

## Purpose

`SimpleMockNodeManager` is a minimal `NodeManager` implementation for tests that need controllable node status, pipeline counts, and container sets without the heavier behavior of `MockNodeManager`. Its own TODO notes it overlaps with `MockNodeManager` and exists because decommission/maintenance support made the older mock hard to refactor.

## Important APIs, Types, and Functions

- `register(DatanodeDetails, NodeStatus)` stores a `DatanodeInfo` and persists operational state fields onto the datanode details.
- `setNodeStatus` mutates a registered node's health and operational status.
- `setNodeOperationalState` updates operational state or throws `NodeNotFoundException`.
- `setPipelines` creates synthetic `PipelineID` sets; `getPipelines` returns null when empty to mirror SCM behavior.
- `setContainers` and `getContainers` manage datanode-to-container sets, returning an empty set by default.
- `getPendingContainerTracker` lazily creates a tracker; `checkSpaceAndRecordAllocation` always returns true.

## Control Flow and State Behavior

The implementation is map-backed: `nodeMap`, `pipelineMap`, and `containerMap` are concurrent maps keyed by `DatanodeID`. Registration and status changes update both the map and the persisted operational-state fields in `DatanodeDetails`. Most `NodeManager` interface methods below the functional core are placeholders that return null, zero, empty maps, or no-op, making the class suitable only for narrow tests that call the implemented subset.

## State and Persistence

All state is in-memory and local to the mock. It mutates `DatanodeDetails` persisted state fields for realistic status behavior but writes no external storage.

## Dependencies and Integration Points

It depends on `DatanodeInfo`, `NodeStatus`, `PipelineID`, `ContainerID`, `PendingContainerTracker`, and the `NodeManager` interface. Integration points are tests for replication, container placement, or node-state decisions that do not require full topology, storage metrics, heartbeat, or command-queue behavior.

## Risks and Test Signals

The main risk is accidental use in code paths requiring unimplemented `NodeManager` methods, where null or zero defaults can hide bugs or cause unrelated failures. The useful signal is precise control over node operational state, pipeline presence, and container membership with minimal fixture cost.
