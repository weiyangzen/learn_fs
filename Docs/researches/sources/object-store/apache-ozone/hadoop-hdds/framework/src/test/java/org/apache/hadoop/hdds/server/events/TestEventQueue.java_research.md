<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueue.java

Purpose: tests core event queue behavior: single event dispatch, multiple subscribers, fixed-thread-pool affinity executor scheduling, queue accounting, and non-power-of-two queue selection.

Important APIs/types/functions: `EventQueue`, `TypedEvent`, `EventHandler`, `EventPublisher`, `EventExecutor`, `FixedThreadPoolWithAffinityExecutor`, `EventQueue.getExecutorName`, `queuedEvents`, `scheduledEvents`, `successfulEvents`, `fireEvent`, and `processAll`.

Control flow: `startEventQueue` creates a fresh queue and `stopEventQueue` closes it. Tests register handlers, fire typed events, call `processAll` with timeouts, and inspect handler side effects or executor counters. The affinity test injects a `LinkedBlockingQueue` and fires multiple values, then checks queue length, scheduled/successful counts, and summed payloads. A `TrackingQueue` subclass records which internal queues receive items.

State and persistence behavior: state is in-memory event queues, handler arrays, atomic counters, executor metrics, and tracking sets. No disk persistence.

Dependencies and integration points: integrates HDDS event abstractions with Java concurrent queues, atomics, concurrent maps, and AssertJ/JUnit assertions.

Risks: async processing and timing can be flaky under slow environments; timeout values need enough headroom. Queue-affinity behavior is implementation-specific and should be updated if scheduling changes intentionally.

Test signals: asserts payload delivery, multiple subscribers receive the same event, queued/scheduled/successful event counts, aggregate event totals, and all queues are selected for non-power-of-two queue counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/TestEventQueue.java -->
