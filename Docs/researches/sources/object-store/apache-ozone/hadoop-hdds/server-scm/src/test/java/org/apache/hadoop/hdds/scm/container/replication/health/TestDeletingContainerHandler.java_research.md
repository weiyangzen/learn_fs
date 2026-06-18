<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestDeletingContainerHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestDeletingContainerHandler.java

Purpose: verifies `DeletingContainerHandler`, which advances DELETING containers to deleted state when replicas are gone and sends delete commands for remaining empty replicas lacking pending deletes.

Important APIs and types: `DeletingContainerHandler`, `ContainerCheckRequest`, `ContainerReplicaOp.PendingOpType.DELETE`, `ReplicationManager.updateContainerState`, `ReplicationManager.sendDeleteCommand`, `ECReplicationConfig`, and `RatisReplicationConfig`.

Control flow: negative tests cover non-DELETING EC/RATIS containers. Cleanup tests build DELETING containers with no replicas and verify read-only mode suppresses state update while normal mode updates. Delete-resend tests compare replicas with complete pending deletes, partial pending deletes, and no pending deletes. Non-empty replicas must not receive delete commands.

State and persistence behavior: modeled state is lifecycle transition to deleted and pending delete operations. Read-only requests must not mutate lifecycle state. The handler only sends deletes for empty replicas, avoiding data loss.

Dependencies and integration points: integrates container lifecycle, pending-op tracking, replica emptiness, EC/RATIS replica indexes, and replication-manager command APIs.

Risks: resending deletes without checking pending ops can duplicate work; deleting non-empty replicas would be unsafe; failing to mark no-replica containers deleted can leave stale metadata.

Test signals: handler return values, lifecycle update invocation counts, and delete-command counts for RATIS and EC cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestDeletingContainerHandler.java -->
