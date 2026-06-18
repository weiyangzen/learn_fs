# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/states/TestNodeStateMap.java

Purpose: unit-tests `NodeStateMap`, the internal map used by `NodeStateManager` to track datanode details, health/operational state combinations, and per-node container lists.

Important APIs and types: uses `NodeStateMap`, `DatanodeInfo`, `DatanodeDetails`, `DatanodeID`, `NodeStatus`, `NodeOperationalState`, `NodeState`, `ContainerID`, and exceptions `NodeAlreadyExistsException` and `NodeNotFoundException`.

Control flow: helper methods add a generated datanode with a given `NodeStatus`. Tests add and retrieve nodes, update health while preserving operational state/expiry, update operational state while preserving health, generate one node for every op-state/health combination, and query counts by exact status and partial op/health filters. The concurrency test iterates a node's container collection while another thread removes an element.

State and persistence behavior: all state is in-memory. The map maintains indexes for total nodes, status-specific lists, datanode info lookup, and containers per datanode. Health and operational-state updates return the new status and update subsequent lookups. Container iteration is expected to tolerate concurrent mutation without surfacing an exception.

Dependencies and integration points: depends on `DatanodeInfo` construction with layout/roll interval values from `HddsTestUtils`, and on Ozone container ID value objects.

Risks and edge cases: `NodeOperationalState.values()` and `NodeState.values()` drive expected counts, so adding enum values changes asserted totals. The concurrency test only checks for thrown exceptions, not deterministic iteration content.

Test signals: strong low-level signal for node-state indexing correctness, expiry preservation, partial count APIs, and safe container-list iteration during concurrent modifications.
