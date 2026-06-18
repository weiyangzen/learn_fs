<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/RatisContainerSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/RatisContainerSafeModeRule.java

Purpose: `RatisContainerSafeModeRule` specializes the container safe-mode rule for Ratis containers. It treats one reported replica as the minimum requirement.

Important APIs and types: It extends `AbstractContainerSafeModeRule`, returns `ReplicationType.RATIS`, and implements `handleReportedContainer`.

Control flow: On a reported container, it looks up the base map's minimum replica value. If the container is still tracked, it removes it, asserts that the minimum replica value is exactly one, increments the satisfied count, and updates the one-replica metric.

State and persistence behavior: Runtime state is inherited from the base class. The class writes no durable state.

Dependencies and integration points: It depends on Ratis container replication configs having `getMinimumNodes() == 1` for safe-mode read availability and on datanode container registration reports.

Risks: The Ratis precondition assertion will fail if a future Ratis config reports a different minimum node count. Duplicate reports after removal are ignored. Empty containers are excluded by the base initializer.

Test signals: Tests should cover first report satisfying a tracked container, duplicate reports no-op, assertion of minimum replica one, metric increments, and base threshold behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/RatisContainerSafeModeRule.java -->
