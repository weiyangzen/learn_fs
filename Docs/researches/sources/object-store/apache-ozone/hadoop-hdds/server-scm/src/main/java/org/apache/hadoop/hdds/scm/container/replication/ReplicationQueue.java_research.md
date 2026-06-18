<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationQueue.java

## Purpose

`ReplicationQueue` encapsulates ReplicationManager's under-replicated and over-replicated work queues. It gives processors a small API for enqueue/dequeue and size inspection while preserving prioritization for under-replicated containers.

## Important APIs, Types, and Functions

Public methods are overloaded `enqueue`, `dequeueUnderReplicatedContainer`, `dequeueOverReplicatedContainer`, `underReplicatedQueueSize`, `overReplicatedQueueSize`, and `isEmpty`. The under queue stores `UnderReplicatedHealthResult`; the over queue stores `OverReplicatedHealthResult`.

## Control Flow

Under-replicated results go into a synchronized priority queue ordered by weighted redundancy and then requeue count. Re-enqueue increments the result's requeue count, reducing its priority after a failed processing attempt. Over-replicated results use a synchronized FIFO `LinkedList`.

## State and Persistence Behavior

All state is in-memory queue state rebuilt periodically by ReplicationManager health scans. Duplicate entries can occur if a result is requeued while the queue is refreshed; later processing observes pending ops and naturally discards no-op duplicates.

## Dependencies and Integration Points

It integrates with health check handlers that enqueue results and with `UnderReplicatedProcessor`/over-replicated processors that dequeue and command datanodes. Metrics read queue sizes through `ReplicationManagerMetrics`.

## Risks and Edge Cases

The synchronized queue wrapper protects single queue operations, not compound workflows. Requeue count mutates the health result object. Duplicate entries are accepted by design, relying on periodic refresh and idempotent replication processing.

## Test Signals

Tests should assert under-replication priority ordering by weighted redundancy then requeue count, requeue-count increment on enqueue, FIFO behavior for over-replicated results, null dequeue on empty queues, and size/is-empty consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationQueue.java -->
