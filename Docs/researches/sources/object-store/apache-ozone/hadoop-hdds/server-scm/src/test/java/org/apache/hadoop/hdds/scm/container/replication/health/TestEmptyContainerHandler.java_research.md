<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestEmptyContainerHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestEmptyContainerHandler.java

Purpose: tests `EmptyContainerHandler`, which detects empty closed/quasi-closed containers and deletes their replicas before updating container state.

Important APIs and types: `EmptyContainerHandler`, `ContainerCheckRequest`, `ReplicationManager.sendDeleteCommand`, `ReplicationManager.updateContainerState`, `ContainerHealthState.EMPTY`, `ECReplicationConfig`, `RatisReplicationConfig`, and lifecycle states `CLOSED`, `CLOSING`, `QUASI_CLOSED`.

Control flow: tests verify empty closed EC and RATIS containers return true, increment `EMPTY`, send delete commands in normal mode, and suppress commands in read-only mode. Non-closed empty containers, non-empty containers, and empty containers with a non-empty replica return false. Empty containers with no replicas still count as empty. A sequence-id test ensures state is not updated when no replica sequence matches the container. Quasi-closed RATIS empty containers are also handled.

State and persistence behavior: no durable state changes occur, but lifecycle update calls are verified. Empty is defined by key count rather than bytes used, and replica emptiness must agree before deletion. Read-only mode only reports.

Dependencies and integration points: integrates replica key/byte metadata, sequence ID checks, delete commands, lifecycle events, and report counters.

Risks: deleting replicas for a container that only appears empty due to stale metadata would be unsafe. The sequence-id guard prevents advancing state based on unrelated stale replicas.

Test signals: handler result, delete-command counts, `EMPTY` report count, lifecycle update calls, read-only behavior, and sequence-id mismatch behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestEmptyContainerHandler.java -->
