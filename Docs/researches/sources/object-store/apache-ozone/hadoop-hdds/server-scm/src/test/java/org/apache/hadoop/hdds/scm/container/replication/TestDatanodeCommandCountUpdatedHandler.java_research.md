# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestDatanodeCommandCountUpdatedHandler.java

Purpose: This focused test verifies that `DatanodeCommandCountUpdatedHandler` forwards datanode command-count update events to `ReplicationManager`.

Important APIs and types: It uses `DatanodeCommandCountUpdatedHandler`, `ReplicationManager`, `DatanodeDetails`, `MockDatanodeDetails`, and Mockito verification.

Control flow: Setup creates a mocked replication manager and handler. The test generates one datanode, invokes `handler.onMessage(datanode, null)`, and verifies that `replicationManager.datanodeCommandCountUpdated(datanode)` is called.

State and persistence behavior: There is no persistence and no meaningful internal state beyond the handler's reference to `ReplicationManager`.

Dependencies and integration points: The handler sits in the SCM event path where datanode command-count changes are reported and replication manager may use updated counts for throttling or scheduling decisions.

Risks: The test only verifies forwarding and does not cover null datanodes, publisher usage, event registration, or downstream replication-manager behavior.

Test signals: A single Mockito verification that the exact datanode object is passed to `datanodeCommandCountUpdated`.
