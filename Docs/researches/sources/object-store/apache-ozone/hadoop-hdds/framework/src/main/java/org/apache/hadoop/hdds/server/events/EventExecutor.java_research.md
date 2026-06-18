# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventExecutor.java

## Purpose

`EventExecutor<PAYLOAD>` defines how an event handler is invoked and monitored by the HDDS event queue. Executors provide thread separation while guaranteeing that a single handler is not executed concurrently by multiple threads.

## Important APIs, Types, and Functions

`onMessage(EventHandler<PAYLOAD>, PAYLOAD, EventPublisher)` schedules or invokes handler processing. Metrics methods expose failed, successful, queued, scheduled, dropped, long-wait, and long-execution event counts. `getName()` returns a human-readable executor name. It extends `AutoCloseable`.

## Control Flow

`EventQueue` delegates event delivery to an executor, which decides synchronous/asynchronous scheduling, failure accounting, and downstream publishing through the supplied publisher.

## State and Persistence Behavior

The interface defines metric state but not storage. Implementations keep counters and queues in memory; no persistence is implied.

## Dependencies and Integration Points

It integrates event handlers and publishers with monitoring and lifecycle cleanup in the server event framework.

## Risks and Edge Cases

The non-concurrent-per-handler guarantee is documented here and must be enforced by implementations. Default dropped/long-wait/long-execution methods return zero, so older implementations may hide those metrics.

## Test Signals

Executor implementation tests should cover serialization per handler, success/failure counters, queued/scheduled counters, close behavior, dropped-event accounting, long wait/execution thresholds, and publisher use by handlers.
