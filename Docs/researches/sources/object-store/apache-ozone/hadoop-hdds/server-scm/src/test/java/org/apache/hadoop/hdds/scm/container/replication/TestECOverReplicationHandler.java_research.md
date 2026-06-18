# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECOverReplicationHandler.java

Purpose: Tests `ECOverReplicationHandler`, which removes excess erasure-coded container replicas by replica index. The scenarios prove the handler deletes only redundant EC indexes, ignores replicas that should not count toward actionable excess, and can process over-replicated indexes even when the health object is an under-replicated result.

Important APIs and types: Uses `ECOverReplicationHandler`, `ContainerHealthResult.OverReplicatedHealthResult`, `UnderReplicatedHealthResult`, `DeleteContainerCommand`, `ContainerReplicaOp.PendingOpType.DELETE`, `NodeStatus`, `PlacementPolicy.replicasToRemoveToFixOverreplication`, and `ReplicationManager.sendThrottledDeleteCommand`. `MockNodeManager`, `NodeSchemaManager`, and `ReplicationTestUtil.mockRMSendThrottledDeleteCommand` supply topology and command capture.

Control flow: `setup` builds a closed `rs-3-2` container, a mocked replication manager that can mark one node stale, a simple placement policy, and a command set. Tests first prove no deletion when indexes 1-5 are present exactly once, when overage is fixed by pending delete, or when extra replicas are decommissioning, stale, or open. Other tests create duplicate index groups and assert delete counts per index. A defensive policy test returns a replica with the wrong index and expects no unsafe delete. Delete throttling injects an overloaded exception on the first send while confirming later eligible work can still be captured.

State and persistence behavior: The handler is observed through in-memory command generation. Replica index distribution is the key state; `staleNode` changes mocked node status, pending ops reduce actionable overage, and the command set records generated `DeleteContainerCommand`s with nonzero EC replica indexes.

Dependencies and integration points: Covers interaction with node health, placement policy, pending op accounting, replication manager delete throttling, and EC index semantics. It also exercises the integration path where an under-replicated health result is sent to the over-replication handler to resolve excess duplicate indexes.

Risks and test signals: Risks include deleting stale/open/decommissioning replicas incorrectly, deleting the wrong EC index, failing to honor pending deletes, and losing retry behavior on throttling. Signals are exact command counts, per-index delete accounting, nonzero replica-index assertions, and exception-path checks.
