# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/MockNodeManager.java

## Purpose

`MockNodeManager` is a substantial test implementation of the SCM `NodeManager` interface. It supplies synthetic datanodes, storage metrics, network topology, pipeline membership, container membership, pending container allocation accounting, command queues, and node health transitions for SCM container, pipeline, placement, and block-manager tests.

## Important APIs, Types, and Functions

- Constructors create fake nodes, register provided nodes, or initialize from `DatanodeUsageInfo` and container sets.
- `getNodes`, `getAllNodes`, `getNodeCount`, `getStats`, `getNodeStats`, `getUsageInfo`, and `getDatanodeInfo` expose node inventory and storage reports.
- `checkSpaceAndRecordAllocation` and `removePendingAllocationForDatanode` delegate to `PendingContainerTracker`.
- `getPipelines`, `addPipeline`, `removePipeline`, `setNode2PipelineMap`, and `pipelineLimit` model pipeline membership.
- `setContainers`, `getContainers`, `addContainer`, `removeContainer`, `addContainer(size)`, and `delContainer(size)` model container placement and capacity changes.
- `register`, `getNode`, `getNodesByAddress`, and `getClusterNetworkTopologyMap` maintain topology and address lookup.
- `addDatanodeCommand`, `onMessage`, `getCommandCount`, and `clearCommandQueue` record commands sent to datanodes.

## Control Flow and State Behavior

The class initializes healthy, stale, and dead node lists based on a static `NodeData` table with capacity and used-space values. Registration adds `DatanodeInfo` to `NodeStateMap`, records DNS/IP-to-UUID mappings, assigns network names, and inserts nodes into `NetworkTopologyImpl`. Node queries synthesize `DatanodeInfo` objects with storage and metadata storage reports from `SCMNodeStat` values. Capacity mutations update both per-node metrics and aggregate metrics.

Pipeline state is tracked by `Node2PipelineMap`; container state by `NodeStateMap`; command state by a `Map<DatanodeID, List<SCMCommand<?>>>`; and pending allocation by `PendingContainerTracker`. Several `NodeManager` methods are intentionally no-op or return simple defaults because the class is a targeted test double rather than a full SCM node manager.

## State and Persistence

All state is in-memory. No SCM DB tables are used. The class simulates persistent-looking datanode reports and topology, but they are rebuilt per test instance.

## Dependencies and Integration Points

`MockNodeManager` integrates with a broad test surface: placement policies, pipeline manager, container manager, block allocation, disk balancer tests, event handlers, `NetworkTopologyImpl`, `DatanodeInfo`, `SCMNodeStat`, `NodeStateMap`, `Node2PipelineMap`, and storage-report helpers from `HddsTestUtils`.

## Risks and Test Signals

Because it returns simplified defaults for many methods, tests using it can miss behavior present in real `SCMNodeManager`. Important risks are stale aggregate metrics after manual mutation, topology lookup assumptions based on default rack paths, and no-op operational state methods. Its value is deterministic, low-overhead integration testing with realistic storage-report and topology enough for placement/allocation code.
