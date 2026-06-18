<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/ECContainerSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/ECContainerSafeModeRule.java

Purpose: `ECContainerSafeModeRule` specializes the container safe-mode rule for erasure-coded containers, requiring reports from at least the EC replication config's minimum number of distinct datanodes.

Important APIs and types: It extends `AbstractContainerSafeModeRule`, returns `ReplicationType.EC`, and tracks per-container datanode IDs in `ecContainerDNsMap`.

Control flow: For each reported container still in the missing-container map, the rule records the reporting datanode in a per-container concurrent map. Once the distinct datanode count reaches the container's minimum replica value, it removes the container, increments the satisfied count, and updates the EC replica-reported metric.

State and persistence behavior: Runtime state includes the base missing-container map plus EC per-container datanode-report maps. Cleanup clears both. No durable state is written.

Dependencies and integration points: It depends on EC `ReplicationConfig.getMinimumNodes()` values captured by the base class and datanode registration reports sent during SCM startup.

Risks: It counts distinct datanodes, not EC replica indexes, so multiple reported indexes on one datanode still count once. Stale entries in `ecContainerDNsMap` remain until cleanup even after a container is satisfied. Missing-container initialization excludes empty containers.

Test signals: Tests should cover distinct datanode counting, duplicate datanode reports, threshold satisfaction at minimum nodes, metrics increments, cleanup of EC maps, and behavior when a reported container is not tracked.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/ECContainerSafeModeRule.java -->
