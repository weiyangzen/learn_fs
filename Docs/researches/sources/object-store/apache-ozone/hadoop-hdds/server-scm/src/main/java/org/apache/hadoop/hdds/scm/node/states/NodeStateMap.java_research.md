# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeStateMap.java

## Purpose
`NodeStateMap` is the thread-safe in-memory map from `DatanodeID` to `DatanodeEntry`, providing node details, status filters, and per-node container membership.

## Important APIs, Types, And Functions
Mutation methods include `addNode`, `removeNode`, `updateNode`, `updateNodeHealthState`, `updateNodeOperationalState`, `addContainer`, `removeContainer`, and `setContainersForTesting`. Read methods include `getNodeInfo`, `getNodeStatus`, `getAllDatanodeInfos`, `getDatanodeDetails`, `getDatanodeInfos`, `getNodeCount`, `getTotalNodeCount`, `getContainers`, and `getContainerCount`. Private helpers `getExisting`, `countNodes`, `filterNodes`, and `matching` centralize locking and predicates.

## Control Flow
All public methods acquire a read or write lock around `nodeMap`. Add rejects duplicate IDs. Update replaces the `DatanodeEntry` for an ID and returns the previous `DatanodeInfo`. Health and operational-state updates mutate the `NodeStatus` inside the existing `DatanodeInfo`. Filtering APIs construct predicate chains for exact `NodeStatus`, operational state, health state, or wildcards.

Container operations delegate to the entry's `TreeSet`. Reads return copies for container sets and collected lists for node sets, so callers receive snapshots. `toString` intentionally reports only total node count and warns that no global consistency is guaranteed.

## State And Persistence Behavior
State is an in-memory `HashMap` protected by a `ReentrantReadWriteLock`. The class does not persist to disk; higher layers rebuild or update it from registration, heartbeat, container report, and pipeline/container events. `DatanodeInfo` objects are returned directly, so object-level mutation can occur outside `NodeStateMap` unless callers respect ownership.

## Dependencies And Integration Points
It depends on `DatanodeInfo`, `NodeStatus`, protobuf node state enums, `DatanodeID`, and `ContainerID`. It is used by `NodeStateManager`, which wraps this low-level map with heartbeat health checking and SCM events.

## Risks And Edge Cases
`updateNode` replaces the full `DatanodeEntry`, dropping existing container membership. That is safe only if callers intentionally rebuild membership or do not care about the old container set. Directly returning `DatanodeInfo` means the map lock does not protect later mutations to that object. Predicate filtering uses snapshots under lock but results can be stale immediately after return.

## Test Signals
Tests should cover duplicate add, missing-node exceptions, node update semantics including container membership replacement, status transitions, wildcard filtering counts, returned container copy isolation, concurrent read/write behavior, and removal followed by lookup.
