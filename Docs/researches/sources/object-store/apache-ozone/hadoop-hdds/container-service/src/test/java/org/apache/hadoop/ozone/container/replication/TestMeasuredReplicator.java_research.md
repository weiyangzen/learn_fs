## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestMeasuredReplicator.java

Purpose: Tests metric accounting wrapper `MeasuredReplicator` for success/failure counts, transferred bytes, replication duration, failure duration, success duration, and queue time.

Important APIs/types/functions: `MeasuredReplicator.replicate`, `AbstractReplicationTask.Status`, metric getters for success/failure bytes and times, and `ReplicationTask.getQueued`.

Control flow: Setup installs a delegate replicator that marks odd container IDs done, even IDs failed, sets transferred bytes to ID * 1024, and sleeps by container ID milliseconds. Tests execute tasks and assert counters/timers include only the correct status class. Queue-time test overrides `getQueued` to one second in the past.

State and persistence behavior: Metrics are in-memory and closed after each test.

Dependencies and integration points: Provides coverage for supervisor-visible metrics around any `ContainerReplicator` implementation.

Risks and test signals: Sleep-based timing assertions may be slow or slightly noisy but use lower bounds. The tests guard against mixing success/failure byte and time counters.
