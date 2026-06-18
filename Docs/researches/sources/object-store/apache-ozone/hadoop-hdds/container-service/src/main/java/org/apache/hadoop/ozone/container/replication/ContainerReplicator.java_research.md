# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerReplicator.java

Purpose: small strategy interface for executing a `ReplicationTask`.

Important APIs and types: `replicate(ReplicationTask task)` is the only method. Implementations in this package include pull (`DownloadAndImportReplicator`), push (`PushReplicator`), and metric-wrapped (`MeasuredReplicator`) strategies.

Control flow and state: none in the interface. Implementations are responsible for setting the task status and transferred bytes.

Dependencies and integration: `ReplicationTask.runTask()` delegates here, and `ReplicationSupervisor` observes the final task status for counters.

Risks and test signals: a replicator that returns without setting `DONE`, `FAILED`, or `SKIPPED` can skew supervisor metrics. Tests should verify every implementation sets status on success and failure and handles interrupted/network exceptions consistently.
