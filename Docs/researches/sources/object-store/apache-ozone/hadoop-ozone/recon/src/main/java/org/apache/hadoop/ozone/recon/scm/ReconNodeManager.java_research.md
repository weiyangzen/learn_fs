## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconNodeManager.java

Purpose: `ReconNodeManager` is Recon's persistent node manager. It subclasses SCM's `SCMNodeManager` but restricts commands and stores DataNode identity in Recon's SCM DB.

Important APIs and types: constructors accept `OzoneConfiguration`, `SCMStorageConfig`, event queue/publisher, `NetworkTopology`, the `NODES` table, layout manager, and optionally `ReconContext`. Key methods include `loadExistingNodes`, `addNodeToDB`, `processHeartbeat`, `register`, `updateNodeOperationalStateFromScm`, `reinitialize`, `removeNode`, and `sendFinalizeToDatanodeIfNeeded`.

Control flow: on startup, `loadExistingNodes` iterates the persisted node table and registers each node in memory using max layout versions. Heartbeats update `datanodeHeartbeatMap`; if a node is new or has not refreshed within three Recon heartbeat intervals, Recon asks it to re-register. Command processing only passes `reregisterCommand` to the parent and filters all other commands. Registration updates the DB for already-known nodes, delegates to parent registration, and updates `ReconContext` health based on topology validity.

State and persistence: durable state is `nodeDB`, a RocksDB table keyed by `DatanodeID`. Runtime state includes inherited node state structures and `datanodeHeartbeatMap`. `removeNode` deletes both parent in-memory state and DB entry. `reinitialize` swaps the table handle after SCM snapshot replacement and reloads nodes.

Dependencies and integration points: used by the facade, DataNode protocol server, node report handler, stale/dead/new-node handlers, pipeline manager, placement policy, and Recon APIs. `ReconDeadNodeHandler` calls `updateNodeOperationalStateFromScm` to align operational state with authoritative SCM.

Risks and edge cases: `loadExistingNodes` calls `register` with null reports; parent assumptions must remain compatible. `datanodeHeartbeatMap` is a `HashMap` accessed from heartbeat/event threads without synchronization, which is a concurrency risk. Only reregister commands are allowed, so any future command needed by Recon must be explicitly added. Invalid topology errors update global health and return an error response rather than throwing.

Test signals: API and SCM facade tests instantiate or mock the facade that owns this manager. Focused tests should cover restart reload from `NODES`, heartbeat reregister threshold, command filtering, invalid topology health updates, and concurrent heartbeat safety.
