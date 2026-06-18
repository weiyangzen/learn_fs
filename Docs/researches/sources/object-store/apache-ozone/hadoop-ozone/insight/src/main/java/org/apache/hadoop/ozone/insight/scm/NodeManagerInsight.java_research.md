<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/NodeManagerInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/NodeManagerInsight.java

Purpose: insight point for SCM datanode management and node report/heartbeat processing.

Important APIs: `getRelatedLoggers` returns the `SCMNodeManager` logger. `getMetrics` builds node-counter metrics for every combination of `NodeOperationalState` and `NodeState`, plus heartbeat processed and heartbeat processing failed counters. `getDescription` identifies SCM datanode management.

Control flow and integration: enum-driven metric construction tracks generated HDDS protobuf state enums, reducing manual list drift for node state combinations. Metrics are fetched from SCM `/prom`.

State and persistence: stateless. No persistence.

Risks and tests: generated metric names are lower-cased formatted enum names; exporter naming must match exactly. Adding enum values changes displayed metrics automatically and may expose missing exporter support. No direct tests cover this insight.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/NodeManagerInsight.java -->
