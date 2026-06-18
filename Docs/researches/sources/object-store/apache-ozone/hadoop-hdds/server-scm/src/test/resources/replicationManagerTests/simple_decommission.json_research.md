# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/resources/replicationManagerTests/simple_decommission.json

Purpose: This fixture verifies that containers hosted on decommissioning datanodes are treated as under-replicated for both Ratis and EC replication so replacement replicas are scheduled.

Important APIs and types: It contains two scenarios, one `RATIS:THREE` closed container with a decommissioning replica and one `EC:RS-3-2-1024k` closed container with one decommissioning EC index. Both expect `underReplicated` and `underReplicatedQueue` counters and `replicateContainerCommand`.

Control flow: The replication-manager harness loads the scenarios, marks one datanode as `DECOMMISSIONING`, runs the replication check, and verifies that the manager queues replication work even though the nominal replica count still includes the decommissioning node.

State and persistence behavior: Static fixture data only. It models operational state effects in SCM's in-memory replication evaluation.

Dependencies and integration points: It depends on operational-state parsing and the replication-manager command verifier. The EC scenario also depends on replica index handling.

Risks: The fixture covers simple one-node decommission only. It does not cover decommissioned, dead, or mixed maintenance states in the same file.

Test signals: One under-replication queue entry and a replicate command for both Ratis and EC decommission scenarios.
