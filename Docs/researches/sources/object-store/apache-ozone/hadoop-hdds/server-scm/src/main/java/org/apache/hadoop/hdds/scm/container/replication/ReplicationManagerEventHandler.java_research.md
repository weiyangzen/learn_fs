# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerEventHandler.java

Purpose: `ReplicationManagerEventHandler` handles datanode-related events by waking `ReplicationManager` when a node state change may require a new replication scan.

Important APIs and behavior: it implements `EventHandler<DatanodeDetails>`. The constructor stores a `ReplicationManager` and `SCMContext`. `onMessage` returns immediately unless the SCM is leader-ready and not in safe mode, logs the datanode event at debug level, and calls `replicationManager.notifyNodeStateChange()`.

Control flow: this is a guard-and-forward handler. It deliberately mirrors `ReplicationManager` readiness conditions so events do not wake or mutate replication state while SCM cannot safely act.

State and persistence: the handler has only final references to collaborators. It persists no state. Wakeup behavior is controlled by `ReplicationManager.notifyNodeStateChange`, which checks running/service status, monitor thread state, and queue emptiness.

Dependencies and integration: it depends on the Ozone event framework (`EventHandler`, `EventPublisher`), `DatanodeDetails`, `SCMContext`, and `ReplicationManager`. It is intended to be registered for node state events.

Risks: events received while safe mode is active or leadership is not ready are dropped rather than queued; this is acceptable because the monitor will scan later after readiness. If the replication queue is not empty, `ReplicationManager` will decline to wake the monitor to avoid repeated queue replacement during active work.

Test signals: `TestReplicationManagerEventHandler` covers notification forwarding and suppression when SCM is not leader-ready or is in safe mode. `TestDatanodeCommandCountUpdatedHandler` and `ReplicationManager` tests cover related event-driven wakeup behavior.
