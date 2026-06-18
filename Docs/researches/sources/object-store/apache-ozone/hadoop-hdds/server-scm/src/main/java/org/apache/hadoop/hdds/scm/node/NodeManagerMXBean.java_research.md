# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeManagerMXBean.java

Purpose: `NodeManagerMXBean` defines the JMX management view for SCM node manager information.

Important APIs and types: It exposes `getNodeCount`, `getNodeInfo`, `getNodeStatusInfo`, and default `getNodeStatistics`. Return types are string-keyed maps suitable for JMX serialization.

Control flow: The interface has no executable flow beyond the default `getNodeStatistics`, which returns an empty map. Implementations are expected to build node counts by health/operational state, disk metrics, status table entries, and optional statistics.

State and persistence behavior: The MXBean reads current node-manager state and exposes snapshots. It does not persist anything.

Dependencies and integration points: `NodeManager` extends this interface, allowing its implementation to register with JMX/metrics management. It uses `InterfaceAudience.Private` to mark it internal to Ozone.

Risks: String-keyed nested maps are flexible but not type-safe; changing key names can break dashboards and tests. The default empty statistics map can mask missing implementation support.

Test signals: Tests should verify that implementation maps contain expected state buckets, disk metrics, status fields, and optional statistics keys without null structures.
