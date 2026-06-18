# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestOverReplicatedProcessor.java

Purpose: Tests `OverReplicatedProcessor`, the queue processor that drains over-replicated health results and delegates actual repair to `ReplicationManager.processOverReplicatedContainer`.

Important APIs and types: Uses `OverReplicatedProcessor`, `ReplicationQueue`, `ReplicationManager`, `ReplicationManagerConfiguration`, `OverReplicatedHealthResult`, `ECReplicationConfig`, and `ContainerInfo`.

Control flow: Setup creates a real `ReplicationQueue`, mocked replication manager, `OverReplicatedProcessor`, and EC container config. It forces `shouldRun()` true and deliberately configures in-flight replication count higher than the limit to show that over-replication processing is not blocked by add/replication limits because over-rep handlers delete. `testSuccessfulRun` enqueues one over-replicated result, mocks successful processing, runs `processAll`, and expects the queue to empty. `testMessageReQueuedOnException` makes processing throw, then asserts the same health result remains queued and is not replaced.

State and persistence behavior: State is entirely queue-local. The queue size and dequeued object identity are the observable persistence-like behavior. No SCM metadata or durable state is modified.

Dependencies and integration points: Integrates queue scheduling with `ReplicationManager.shouldRun`, configured over-replicated interval supplier, and the `processOverReplicatedContainer` handoff. It intentionally checks that replication in-flight limits do not suppress delete-only work.

Risks and test signals: Risks include losing queued work on handler exceptions, over-rep processing being starved by replication limits, and repeated processing after one failure. Signals are queue size, object identity after requeue, and successful emptying on normal completion.
