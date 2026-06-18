# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeReportHandler.java

Purpose: `NodeReportHandler` handles datanode node-report events and forwards storage/metadata report content to `NodeManager`.

Important APIs and types: It implements `EventHandler<SCMDatanodeHeartbeatDispatcher.NodeReportFromDatanode>`. It depends on `NodeManager.processNodeReport`, `DatanodeDetails`, and `NodeReportProto`.

Control flow: The constructor requires a non-null node manager. `onMessage` requires a non-null event object and datanode details, then calls `nodeManager.processNodeReport(dn, report)`.

State and persistence behavior: This handler has no mutable state beyond its node-manager reference. State updates occur inside the node manager, which refreshes datanode storage reports and derived stats.

Dependencies and integration points: It is part of heartbeat dispatch: datanode reports are unpacked by `SCMDatanodeHeartbeatDispatcher`, routed through the event bus, and applied to node-manager state.

Risks: Null events or missing datanode details fail fast with `NullPointerException`, which is appropriate for malformed internal events but may surface if dispatcher contracts change. It does not catch node-manager exceptions.

Test signals: Tests should verify non-null validation and exact forwarding of datanode details plus report to `processNodeReport`.
