<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestMismatchedReplicasHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestMismatchedReplicasHandler.java

Purpose: verifies `MismatchedReplicasHandler`, which sends close commands to replicas whose state does not match a closed or quasi-closed container while letting later handlers continue health processing.

Important APIs and types: `MismatchedReplicasHandler`, `ContainerCheckRequest`, `ReplicationManager.sendCloseContainerReplicaCommand`, `ECReplicationConfig`, `RatisReplicationConfig`, `ContainerReplicaProto.State`, and container sequence IDs.

Control flow: tests confirm open containers and already-healthy closed EC/RATIS containers return false without commands. Mismatched EC and RATIS replicas in OPEN/CLOSING state get close commands, while UNHEALTHY replicas do not. The handler always returns false so under/over-replication handlers can continue. Quasi-closed RATIS mismatches are closed without force. Quasi-closed replicas of closed containers are force-closed only when sequence IDs match. A BCSID-focused case verifies force behavior for quasi-closed matching sequence and non-force behavior for open/closing replicas with older or matching sequence.

State and persistence behavior: no persistent state; the side effect is close-command dispatch. Read-only requests do not generate additional commands.

Dependencies and integration points: integrates replica-state cleanup with replication-manager close-command APIs and downstream health-handler chaining.

Risks: returning true would short-circuit later repair. Force-close semantics differ by replication type and replica state, and incorrect sequence handling can close the wrong data.

Test signals: command invocation counts and force flags, negative checks for unhealthy replicas, read-only suppression, and explicit false return values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestMismatchedReplicasHandler.java -->
