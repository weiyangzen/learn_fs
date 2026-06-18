# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/FixedThreadPoolWithAffinityExecutor.java

Purpose: `FixedThreadPoolWithAffinityExecutor` is an `EventExecutor` for high-volume events where payloads should be partitioned across fixed queues while preserving affinity by `hashCode()`. It is used for report-processing paths such as container reports.

Important APIs/types/functions: the constructor receives a name, event handler, shared work queues, publisher, payload class, executor list, and class-to-executor map. `initializeExecutorPool()` creates one single-thread `ThreadPoolExecutor` per queue. `onMessage()` hashes the payload to a queue and increments metrics. `ContainerReportProcessTask` drains queues and calls the appropriate executor's handler. `IQueueMetrics` lets custom queues report dropped items.

Control flow: construction registers this executor under `clazz.getName()` and starts a queue-draining task on each thread pool if not already active. `onMessage()` enqueues payloads by `Math.floorMod(message.hashCode(), workQueues.size())`. Worker tasks poll queues, find the executor by payload runtime class, inspect `IEventInfo` for creation time/id, update scheduled/done/failed/long-wait/long-execution counters, and log slow events.

State and persistence: in-memory queues, thread pools, an `AtomicBoolean isRunning`, and Metrics2 counters. No durable state. `close()` flips running false, shuts down executors, clears the shared executor map, and unregisters metrics.

Dependencies/integration: depends on `EventExecutor`, `EventHandler`, `EventPublisher`, `IEventInfo`, Metrics2, Guava thread factories, Hadoop `Time`, and SCM event threshold defaults. Used by SCM report-processing tests and integration paths.

Risks: unchecked casts from `P` to `Q` and raw executor-map typing require payload class discipline. `queue.add()` can throw if a bounded queue is full unless the queue handles drops internally. Affinity depends on stable, well-distributed `hashCode()`. Clearing a shared executor map on close can affect other executors if they share it.

Test signals: `TestEventQueue` exercises fixed-pool dispatch, affinity queues, and drop metrics; SCM integration tests instantiate it for container and incremental report handling.
