<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestUnderReplicatedProcessor.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestUnderReplicatedProcessor.java

Purpose: tests the queue processor that drains under-replicated work and delegates each item to `ReplicationManager.processUnderReplicatedContainer`.

Important APIs and types: `UnderReplicatedProcessor`, `ReplicationQueue`, `UnderReplicatedHealthResult`, `ReplicationManagerMetrics`, `ReplicationManager.getReplicationInFlightLimit`, and `ReplicationManager.getInflightReplicationCount`.

Control flow: setup uses a real queue and metrics object with a mocked manager that should run. One test confirms successful processing removes the queued result. Another makes processing throw `IOException`, expecting the same result to be requeued. A limit test sets in-flight count above the global limit, verifies no processing and requeue, then lowers the count and verifies processing succeeds.

State and persistence behavior: queue contents and metrics are the state under test. No durable persistence is involved. The pending-replication-limit-reached metric increments when processing is deferred by the global in-flight limit.

Dependencies and integration points: connects queue scheduling to replication-manager execution and metrics. It depends on `UnderReplicatedHealthResult` priority state only enough to enqueue/dequeue.

Risks: exception handling must preserve the original work item or replication work can be lost. In-flight limit logic must avoid both starvation and overload.

Test signals: queue size, object identity after requeue, manager invocation counts, and metric increment verify the processor's retry and throttling contracts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestUnderReplicatedProcessor.java -->
