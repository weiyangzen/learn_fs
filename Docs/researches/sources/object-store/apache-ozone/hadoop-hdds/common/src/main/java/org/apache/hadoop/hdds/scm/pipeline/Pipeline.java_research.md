# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/pipeline/Pipeline.java

## Purpose
`Pipeline` models the ordered set of datanodes used to store or read a container, together with replication configuration, pipeline lifecycle state, leader identity, optional suggested leader, creation time, state-entry time, replica indexes, and topology-based node order. SCM pipeline managers, container allocation, clients, and datanode protocol calls use it as the core transfer object for placement and routing.

## Important APIs and types
- `getCodec()` exposes a DB codec backed by `HddsProtos.Pipeline`. The codec intentionally does not round-trip equality because the delegated deserializer resets the creation timestamp to `Instant.now()`.
- Accessors expose `PipelineID`, `ReplicationType`, `ReplicationConfig`, `PipelineState`, datanode set/list, ordered read list, leader node, suggested leader, replica index map, and timestamps.
- `getFirstNode`, `getClosestNode`, and `getLeaderNode` choose datanodes for RPC routing. `getClosestNode` prefers `nodesInOrder` when present and falls back to insertion order.
- `copyForRead` converts non-standalone pipelines into standalone read pipelines while preserving factor where possible. `copyForReadFromNode` narrows a pipeline to one datanode and carries its EC replica index.
- `getProtobufMessage` and `toBuilder(HddsProtos.Pipeline)` preserve legacy and newer protobuf fields: string leader IDs, 128-bit UUIDs, `DatanodeID` proto, EC replication config, legacy factor, member replica indexes, and compact member order indexes.
- `Builder` constructs immutable-ish instances, regenerates pipeline ID when nodes change, reconstructs node order from protobuf member order indexes, and validates required fields.
- `PipelineState` maps between Java states `ALLOCATED`, `OPEN`, `DORMANT`, `CLOSED` and protobuf lifecycle values.

## Control flow and state
Most object fields are final and copied into immutable Guava collections, but `leaderId`, `creationTimestamp`, and `nodeStatus` values are mutable through package-visible or public methods. `reportDatanode` updates per-node last-report timestamps and accepts reports from a restarted datanode with matching node values even if the exact object key differs. `isHealthy` treats EC pipelines as healthy by definition, while non-EC pipelines require all nodes to have reported and a leader to be known.

Serialization builds member and replica-index lists in map iteration order and optionally serializes `nodesInOrder` as indexes into the member list. Deserialization rebuilds the member map first, then applies member-order indexes if present. Equality uses only ID, replication config, and node set, while hash code includes the `nodeStatus` map, which is risky because report timestamps can change after construction.

## Dependencies and integration points
The class integrates with `DatanodeDetails`, `DatanodeID`, replication config classes, SCM database codecs, protobufs, client-version-aware port filtering, Jackson JSON annotations, and Ratis preconditions. It is consumed by container protocol clients for datanode selection, by SCM pipeline management for lifecycle transitions, and by DB persistence.

## Risks and test signals
Tests should cover protobuf compatibility across leader ID encodings, EC replica index preservation, node-order round trips, empty/all-excluded node selection errors, ID regeneration on node changes, and health behavior for EC versus Ratis/standalone. The mutable `nodeStatus` versus hash-code behavior is a regression risk if `Pipeline` is used as a hash-map key after reports arrive. The codec timestamp reset is intentional and should be asserted rather than treated as a serialization bug.
