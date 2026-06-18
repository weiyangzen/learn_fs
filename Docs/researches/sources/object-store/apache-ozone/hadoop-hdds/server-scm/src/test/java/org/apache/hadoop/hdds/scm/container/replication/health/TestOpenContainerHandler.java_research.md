<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestOpenContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestOpenContainerHandler.java

Purpose: This test suite verifies `OpenContainerHandler`, the replication-health handler that recognizes SCM containers still in `OPEN` state and decides whether they should remain open or be closed by Replication Manager. It covers both EC and Ratis replication configs.

Important APIs and types: The tests build `ContainerInfo` and `ContainerReplica` sets with `ReplicationTestUtil`, `ECReplicationConfig`, `RatisReplicationConfig`, `ContainerCheckRequest`, `ReplicationManagerReport`, and a mocked `ReplicationManager`. The key production calls under observation are `OpenContainerHandler.handle`, `ReplicationManager.hasHealthyPipeline`, and `ReplicationManager.sendCloseContainerEvent`.

Control flow: Setup defaults the mocked replication manager to report a healthy pipeline. Closed containers are ignored. Healthy open containers with open replicas are handled but not closed. Open containers with non-open replica state or no healthy pipeline are handled and, on non-read-only requests, cause one close-container event. The same scenarios are repeated for Ratis containers with replica index `0`.

State and persistence behavior: There is no durable state. Runtime state is the request's container state, replica states, read-only flag, and report counters. The test ensures read-only requests still compute health but do not emit extra close events.

Dependencies and integration points: This is a unit-level guard for the replication health check chain, Replication Manager pipeline knowledge, close-container event dispatch, and `ReplicationManagerReport` statistics.

Risks: The tests rely on Mockito call counts to distinguish mutating and read-only behavior. They do not validate downstream close-event processing or pipeline lookup internals.

Test signals: Key signals are false for closed containers, true for open containers, exactly one close event for unhealthy or no-pipeline non-read-only checks, and one report increment for `OPEN_UNHEALTHY` or `OPEN_WITHOUT_PIPELINE`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestOpenContainerHandler.java -->
