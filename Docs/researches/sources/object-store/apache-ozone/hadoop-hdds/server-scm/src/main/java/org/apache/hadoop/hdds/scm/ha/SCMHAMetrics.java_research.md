# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAMetrics.java

Purpose: Hadoop metrics source that reports whether the current SCM node is the SCM HA leader.

Important APIs and types: `create(nodeId, leaderId)` registers a `MetricsSource` named `SCMHAMetrics`; `unRegister` removes it. `getMetrics` emits a `NodeId` tag and `SCMHALeaderState` gauge. Inner `SCMHAMetricsInfo` stores current values for test visibility.

Control flow: Metrics collection compares the configured current node id with the leader id, sets state to `1` for leader and `0` for follower, then emits the record.

State and persistence behavior: No durable state. Runtime state is the fixed `currNodeId`/`leaderId` pair and last values in `SCMHAMetricsInfo`.

Dependencies and integration points: Registered through Hadoop `DefaultMetricsSystem`; updated from SCM HA leadership notifications.

Risks and test signals: The leader id is captured at construction, so callers must recreate/update metrics when leadership changes. Tests should assert registration, node tag, leader/follower gauge values, unregister behavior, and visible-for-testing getters.
