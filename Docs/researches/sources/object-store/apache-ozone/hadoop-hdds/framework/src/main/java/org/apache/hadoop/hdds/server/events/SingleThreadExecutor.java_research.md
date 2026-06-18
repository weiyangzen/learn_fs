# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/SingleThreadExecutor.java

Purpose: `SingleThreadExecutor` is the default `EventExecutor` used by `EventQueue.addHandler(event, handler)`. It serializes handler invocations for one handler/executor name on a dedicated thread.

Important APIs/types/functions: constructor creates `EventExecutorMetrics` and a Java `ExecutorService` with a named single thread. `onMessage()` increments queued/scheduled/done/failed counters and catches handler exceptions. Counter accessors implement the `EventExecutor` API. `close()` shuts down the executor and unregisters metrics.

Control flow: `EventQueue.fireEvent()` calls `onMessage()`, which enqueues a runnable. The runnable calls the target handler with the original publisher. Handler exceptions are logged and counted without propagating to the publisher.

State and persistence: in-process executor queue and metrics only. There is no explicit await termination in `close()`, so outstanding work may continue until executor shutdown drains according to Java executor semantics.

Dependencies/integration: depends on `EventExecutor`, `EventHandler`, `EventPublisher`, `EventExecutorMetrics`, `Executors`, and SLF4J. Used by default for most event handlers.

Risks: unbounded single-thread executor queue can grow under sustained overload. No dropped/slow-event methods are overridden here beyond basic counters if the `EventExecutor` interface has defaults. Handler latency directly delays later events for that handler.

Test signals: `TestEventQueue` and `TestEventQueueChain` cover default asynchronous dispatch and drain behavior; many component tests rely on this executor through `EventQueue`.
