<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosingContainerHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosingContainerHandler.java

Purpose: tests `ClosingContainerHandler`, responsible for containers in CLOSING state, including replica close commands and state transitions when replicas are absent or only unhealthy.

Important APIs and types: `ClosingContainerHandler`, `ContainerCheckRequest`, `ReplicationManager.sendCloseContainerReplicaCommand`, `ReplicationManager.updateContainerState`, lifecycle events `CLOSE` and `QUASI_CLOSE`, `TestClock`, `ReplicationManagerConfiguration`, `ECReplicationConfig`, and `RatisReplicationConfig`.

Control flow: negative tests ensure non-closing EC/RATIS containers pass through. Other tests ensure unhealthy replicas are not closed, open/closing replicas are sent close commands, read-only mode avoids side effects, empty closing containers close only after a configured timeout, RATIS all-unhealthy closing containers move to quasi-closed, and EC all-unhealthy closing containers move to closed. Parameterized tests verify force-close is true for EC and false for RATIS.

State and persistence behavior: no durable store is modified, but tests verify lifecycle state update calls and report behavior. Time-dependent state uses `TestClock` and `rmConf.getInterval()` to simulate the empty-closing timeout.

Dependencies and integration points: integrates lifecycle state machine events, replication config type, command dispatch, read-only checks, and SCM timing configuration.

Risks: premature state transitions for empty containers can hide late replicas; failing to force-close EC replicas can leave EC containers stuck; closing unhealthy replicas is intentionally avoided.

Test signals: return values, close-command counts and force flags, lifecycle update calls, read-only no-op behavior, and timeout-driven close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosingContainerHandler.java -->
