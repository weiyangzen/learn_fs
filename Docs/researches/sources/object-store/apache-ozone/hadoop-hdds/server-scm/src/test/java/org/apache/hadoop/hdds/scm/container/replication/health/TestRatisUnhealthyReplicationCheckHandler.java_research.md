<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisUnhealthyReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisUnhealthyReplicationCheckHandler.java

Purpose: This suite verifies `RatisUnhealthyReplicationCheckHandler`, which handles Ratis containers whose usable replicas are `UNHEALTHY` or quasi-closed with stale sequence IDs. It deliberately avoids cases owned by the normal Ratis handler.

Important APIs and types: It uses `RatisUnhealthyReplicationCheckHandler`, `ContainerHealthResult.UnderReplicatedHealthResult`, `ContainerHealthResult.OverReplicatedHealthResult`, `ReplicationQueue`, `ReplicationManagerReport`, `ContainerReplicaOp`, `ContainerHealthState.UNHEALTHY`, `UNHEALTHY_UNDER_REPLICATED`, and `UNHEALTHY_OVER_REPLICATED`.

Control flow: Non-Ratis, normally healthy, normally under-replicated, normally over-replicated, and excess-unhealthy-with-sufficient-healthy cases return false. All-unhealthy sets are classified as unhealthy, under-replicated, or over-replicated based on replica count and pending operations. Pending add/delete can prevent queue insertion while still recording the combined unhealthy state. Quasi-closed replicas with correct sequence IDs are ignored, while stale sequence IDs are treated as unhealthy and can produce under/over replication handling.

State and persistence behavior: Runtime-only state includes replica state, sequence ID, pending ops, report counters, and queue sizes. No persistent storage is touched.

Dependencies and integration points: It complements `RatisReplicationCheckHandler` by separating vulnerable unhealthy-replica repair from normal healthy-replica repair, while sharing the same `ContainerCheckRequest`, queue, and report contracts.

Risks: The boundary between "normal Ratis over-replication owns this" and "unhealthy handler owns this" is subtle. Combined report states intentionally replace separate unhealthy plus under/over counters.

Test signals: The tests assert boolean handling, health-result subtype and redundancy values, pending-operation flags, queue sizes, and that only combined unhealthy counters are incremented for under/over unhealthy cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisUnhealthyReplicationCheckHandler.java -->
