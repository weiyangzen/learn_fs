# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/MeasuredReplicator.java

Purpose: wraps a `ContainerReplicator` and publishes per-replicator metrics for queue time, runtime, success/failure count, and transferred bytes.

Important APIs and functions: the constructor registers this object with the default metrics system under `ContainerReplicator/<name>`. `replicate` records queue latency from task queued time, delegates replication, measures elapsed time, and updates success or failure gauges/counters based on final task status. `close` unregisters the metric source. Getter methods expose metric fields for tests.

Control flow and state: the wrapper does not alter task behavior or catch delegate exceptions; supervisor still owns exception handling around task execution. Metrics are updated only for `DONE` and `FAILED`, not `SKIPPED`.

Dependencies and integration: can wrap pull or push replicators before they are passed into `ReplicationTask`.

Risks and test signals: metrics registration names must be unique per name, and delegate exceptions may bypass metric updates if not caught upstream. Tests should verify success/failure accounting, transferred bytes on failure, queue-time increment, unregister behavior, skipped-task behavior, and duplicate registration handling.
