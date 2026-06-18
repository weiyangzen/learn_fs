<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnderReplicatedProcessor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnderReplicatedProcessor.java

## Purpose

`UnderReplicatedProcessor` specializes `UnhealthyReplicationProcessor` for under-replicated health results. It drains the under-replicated queue and delegates repair command generation to `ReplicationManager.processUnderReplicatedContainer`.

## Important APIs, Types, and Functions

It overrides `dequeueHealthResultFromQueue`, `requeueHealthResult`, `inflightOperationLimitReached`, and `sendDatanodeCommands`. The processed type is `ContainerHealthResult.UnderReplicatedHealthResult`.

## Control Flow

The base processor loop calls this subclass to poll `ReplicationQueue.dequeueUnderReplicatedContainer`. If processing fails, the result is requeued through `ReplicationQueue.enqueue`, which increments retry priority state. The inflight limit check compares `ReplicationManager.getInflightReplicationCount` to the configured pending-op limit.

## State and Persistence Behavior

The class owns no durable state. It relies on the queue and pending replica ops for transient coordination. Actual repair work is persisted only indirectly through commands and pending-op tracking maintained by ReplicationManager.

## Dependencies and Integration Points

It integrates with `ReplicationManager`, `ReplicationQueue`, metrics triggered by the base processor, and datanode command generation in under-replication handlers.

## Risks and Edge Cases

If the cluster-level inflight limit is reached, the processor stops the current pass without draining remaining queue entries. Requeued failures lose priority via requeue count but can still duplicate with queue rebuilds.

## Test Signals

Tests should verify correct queue method usage, requeue on exception or overload, stopping when replication inflight limit is reached, and delegation count/exception propagation from `processUnderReplicatedContainer`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnderReplicatedProcessor.java -->
