# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationSupervisor.java

Purpose: schedules, deduplicates, prioritizes, executes, and meters datanode replication tasks.

Important APIs and functions: `Builder` creates default config, clock, and a `ThreadPoolExecutor` backed by `PriorityBlockingQueue`. `addTask` checks queue capacity, initializes metric counters, adds task uniqueness to `inFlight`, increments queue counters, and submits a `TaskRunner`. `nodeStateUpdated` and `setReplicationMaxStreams` resize executor and queue limits, scaling for maintenance/decommission states. Getter methods expose in-flight counts, queue size, max streams, and counters by metric name. `TaskRunner.run` enforces deadline, datanode operational state, and SCM term checks, then sets status to `IN_PROGRESS`, calls `task.runTask`, updates success/failure/skipped/timeout counters, latency metrics, and removes in-flight state.

Control flow and state: `inFlight` is a concurrent set keyed by task equality, preventing duplicate queued/running tasks. Low-priority tasks are submitted but excluded from command queue size counters. Metrics maps are lazily initialized per task metric name. `maxQueueSize` changes when datanode state changes.

Dependencies and integration: consumes `StateContext`, `DatanodeConfiguration`, `ReplicationConfig`, datanode operational state, SCM leader term, and Hadoop metrics rates. It is the execution gate for replication and related reconstruction tasks.

Risks and test signals: early returns in `TaskRunner` leave task status as queued but still decrement counters in finally. Priority ordering depends on `TaskRunner.compareTo`. Tests should cover duplicate task suppression, low-priority exclusion, deadline expiry, out-of-service skip/run flags, stale SCM term skip, exception handling, counter balance, resize order, and latency metric creation.
