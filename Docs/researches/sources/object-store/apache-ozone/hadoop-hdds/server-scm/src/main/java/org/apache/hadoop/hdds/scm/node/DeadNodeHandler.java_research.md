# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DeadNodeHandler.java

Purpose: `DeadNodeHandler` handles `SCMEvents.DEAD_NODE` by cleaning up SCM state associated with a datanode that is currently dead. It closes open containers, destroys pipelines, removes replicas when appropriate, notifies replication manager, clears command queues, updates deleted-block tracking, and removes the node from network topology if it is still dead.

Important APIs and types: It implements `EventHandler<DatanodeDetails>`. Collaborators include `NodeManager`, `PipelineManager`, `ContainerManager`, optional `DeletedBlockLog`, `NetworkTopology`, `ContainerInfo`, `ContainerReplica`, and event types `CLOSE_CONTAINER` and `REPLICATION_MANAGER_NOTIFY`.

Control flow: `onMessage` first re-reads the current `NodeStatus` and ignores stale events if the node is no longer `DEAD`. It closes any OPEN containers by firing `CLOSE_CONTAINER`, closes and deletes pipelines on the node, skips replica and deleted-block cleanup for nodes in maintenance, notifies replication manager for non-maintenance dead nodes, drains the node command queue, and finally rechecks health before removing the node from topology.

State and persistence behavior: The handler mutates in-memory SCM maps, pipeline manager state, container replica membership, command queue state, topology membership, and deleted-block log state. Pipeline/container manager changes may touch their backing metadata stores depending on the implementation. It does not remove `NodeStateManager` entries.

Dependencies and integration points: It depends on node state transitions emitted by `NodeStateManager`. It coordinates with replication manager through an event, with deleted-block cleanup through `DeletedBlockLog.onDatanodeDead`, and with placement policy through topology removal.

Risks: It must tolerate races where a node resurrects while the dead event is being handled; the final health recheck protects topology removal. Maintenance nodes deliberately keep replicas and delete-block commands, so incorrect maintenance state can change replication behavior. Pipeline cleanup catches IO failures and continues, leaving possible stale pipelines.

Test signals: Tests should cover stale dead-event skip, container close event emission, pipeline close/delete calls, maintenance vs non-maintenance replica handling, deleted-block callback, command queue drain, topology removal only when still dead, and `NodeNotFoundException` logging.
