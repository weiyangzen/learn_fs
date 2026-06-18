# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/HealthyReadOnlyNodeHandler.java

Purpose: `HealthyReadOnlyNodeHandler` handles transitions into `HEALTHY_READONLY`, mainly during layout-version mismatch or upgrade finalization. It resends pipeline close commands so containers in CLOSING can reach CLOSED, and ensures the datanode is present in network topology.

Important APIs and types: It implements `EventHandler<DatanodeDetails>` and depends on `NodeManager`, `PipelineManager`, `PipelineID`, `Pipeline`, and `NetworkTopology`.

Control flow: On event, it gets all pipelines for the node, loads each pipeline, logs its state, and calls `pipelineManager.closePipeline` without force deletion. After pipeline handling, it unconditionally adds the node back to topology and verifies the `DatanodeDetails` stored by `NodeManager` has a parent.

State and persistence behavior: It mutates pipeline state by queuing close behavior in the pipeline manager and mutates in-memory topology membership. It does not directly persist node state or pipeline deletion.

Dependencies and integration points: `NodeStateManager` fires this event on layout mismatch, dead/stale restoration to readonly, or forced finalization transitions. Upgrade services rely on this handler to unblock datanode finalization by nudging closing containers.

Risks: `nodeManager.getPipelines` must not return null; the code iterates directly. IOException on one pipeline is logged and does not stop later topology add. The unconditional topology add is intentionally race-safe against dead-node removal, but the parent assertion can fail if topology/node-map integration is broken.

Test signals: Tests should verify close calls for all known pipelines, IOException tolerance, idempotent topology add for existing nodes, parent non-null after re-add, and behavior when a node has no pipelines.
