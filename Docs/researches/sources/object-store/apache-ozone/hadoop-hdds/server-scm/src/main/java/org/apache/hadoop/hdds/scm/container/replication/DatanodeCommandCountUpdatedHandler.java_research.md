# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/DatanodeCommandCountUpdatedHandler.java

Purpose: event handler for `DATANODE_COMMAND_COUNT_UPDATED` notifications.

Important APIs: constructor and `onMessage(DatanodeDetails, EventPublisher)`.

Control flow and state: logs at trace and delegates the datanode to `ReplicationManager.datanodeCommandCountUpdated`. No local persistence or mutation.

Dependencies and integration: wired into SCM event framework; used to wake or inform ReplicationManager when datanode command load changes. Tested by `TestDatanodeCommandCountUpdatedHandler`.

Risks: no null guard for datanode or replication manager; errors propagate from ReplicationManager. Test signals should verify delegation exactly once and no event publisher dependency.
