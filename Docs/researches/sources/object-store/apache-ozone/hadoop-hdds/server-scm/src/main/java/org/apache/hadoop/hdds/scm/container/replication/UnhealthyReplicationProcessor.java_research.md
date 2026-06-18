<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationProcessor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationProcessor.java

## Purpose

`UnhealthyReplicationProcessor` is the reusable runnable loop for queue-driven replication repair processors. It drains a specific health-result queue, enforces inflight limits, synchronizes per-container processing, requeues failures, and sleeps between passes.

## Important APIs, Types, and Functions

Subclasses implement `dequeueHealthResultFromQueue`, `requeueHealthResult`, `inflightOperationLimitReached`, and `sendDatanodeCommands`. Public/visible methods are `processAll`, `run`, and testing-only `runImmediately`.

## Control Flow

`processAll` caches the current inflight limit, repeatedly checks `ReplicationManager.shouldRun`, stops when limits are reached or the queue is empty, and processes each result under `synchronized(containerInfo)`. `CommandTargetOverloadedException` and other exceptions are counted and requeued after the pass. `run` loops until interrupted, optionally processes the queue, waits for the configured interval, and supports immediate wakeup.

## State and Persistence Behavior

State is transient: `runImmediately`, the interval supplier, counters local to a pass, and failed results. No direct persistence occurs, but `sendDatanodeCommands` can update pending ops and trigger command side effects.

## Dependencies and Integration Points

It integrates with `ReplicationManager`, `ReplicationQueue`, `ContainerHealthResult`, metrics for pending limit reached, and processor subclasses for under/over/mis-replication.

## Risks and Edge Cases

The loop handles broad exceptions to keep the processor alive, but repeated failures can churn requeue counts. The inflight limit is sampled once per pass, so fast topology changes are seen on the next pass. Synchronizing on mutable `ContainerInfo` requires all competing paths to honor the same lock.

## Test Signals

Tests should cover draining, failed-result requeue, overload requeue, pending-limit short circuit and metric increment, no work when `shouldRun` is false, container-level synchronization, interrupt shutdown, and `runImmediately` wake behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationProcessor.java -->
