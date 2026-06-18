# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeManager.java

Purpose: `NodeManager` is the central SCM interface for datanode registration, heartbeat processing, node state queries, storage statistics, command delivery, container/pipeline membership, topology access, admin state changes, pending allocation tracking, and MXBean reporting.

Important APIs and types: It extends `StorageContainerNodeProtocol`, `EventHandler<CommandForDatanode>`, `NodeManagerMXBean`, and `Closeable`. Important methods include `register`, `getNodes`, `getNodeCount`, `getAllNodes`, `getStats`, `getNodeStats`, `getMostOrLeastUsedDatanodes`, `getUsageInfo`, `getDatanodeInfo`, `checkSpaceAndRecordAllocation`, `removePendingAllocationForDatanode`, `getNodeStatus`, `setNodeOperationalState`, pipeline/container membership methods, command queue methods, report processing methods, `getNodesByAddress`, `getLastHeartbeat`, `getClusterNetworkTopologyMap`, `removeNode`, `openContainerLimit`, and `getPendingContainerTracker`.

Control flow: As an interface, it defines expected behavior rather than implementing it. Registration can default missing layout info to the current default layout version. Heartbeat/report processing should update node status, reports, command counts, command queues, and layout versions. Admin calls change operational state, while health state transitions are usually driven by `NodeStateManager`.

State and persistence behavior: Implementations own in-memory node, command, topology, pipeline, container, and stats state. Node operational state is the important persistent contract because datanodes store and report it. The interface also exposes pending-container allocations that age in SCM memory to prevent over-allocation between reports.

Dependencies and integration points: This interface sits at the boundary between SCM, datanode RPCs, events, placement policies, pipeline manager, container manager, decommission manager, metrics/JMX, upgrade layout manager, and command send-notification hooks.

Risks: The interface is broad, so implementation changes can affect many subsystems. Some methods return nullable values or default no-ops, which can hide unsupported behavior in tests. Command counts combine datanode-reported queued commands and SCM-side queued commands; consistency depends on locking in implementations.

Test signals: Implementation tests should cover registration with and without layout info, node state/count filters, stats aggregation, usage sorting, command queue accounting, report processing, pending allocation accounting, topology membership, remove-node restrictions, operational-state event firing, and MXBean map contents.
