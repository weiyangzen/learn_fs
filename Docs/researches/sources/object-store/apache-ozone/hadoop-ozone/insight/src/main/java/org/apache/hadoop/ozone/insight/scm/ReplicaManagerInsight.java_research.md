<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ReplicaManagerInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ReplicaManagerInsight.java

Purpose: insight point for SCM `ReplicationManager`, focused on container health, replication/deletion queues, and EC metrics.

Important APIs: `getRelatedLoggers` returns the `ReplicationManager` logger. `getMetrics` builds three SCM metric groups: container state/health counts, EC replication/deletion/reconstruction counters, and general replication manager inflight/queue/command/timeout/deferred counters. `getConfigurationClasses` exposes `ReplicationManager.ReplicationManagerConfiguration` for the config subcommand. `getDescription` identifies the closed-container replication manager.

Control flow and integration: metrics map directly to Prometheus names emitted by replication manager. The configuration class lets `ConfigurationSubCommand` reflect `@Config` annotations and fetch current values from SCM `/conf`.

State and persistence: stateless descriptor builder. No persistence.

Risks and tests: large hardcoded metric catalog can drift from exporter names. `EcReplicasDeletedTotal` is listed twice with the same metric id, causing duplicate display output. No direct tests cover metric duplication or config exposure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ReplicaManagerInsight.java -->
