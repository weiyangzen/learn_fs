
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/FairCallQueue.java

## Purpose

`FairCallQueue` is a multi-level `BlockingQueue` for RPC calls. It stores calls in priority-specific subqueues, uses a pluggable multiplexer to choose dequeue order, tracks overflow counts, and exports queue metrics.

## Important APIs, types, and functions

The constructor creates `priorityLevels` `LinkedBlockingQueue`s, distributing total capacity with remainder assigned to priority `0`, creates overflow counters, installs a `WeightedRoundRobinMultiplexer`, and registers a metrics proxy. Queue operations include `add()`, `put()`, `offer()`, timed `offer()`, `take()`, `poll()`, `peek()`, `drainTo()`, `remainingCapacity()`, `getQueueSizes()`, `getOverflowedCalls()`, and `setMultiplexer()`.

`MetricsProxy` is a namespace singleton implementing `FairCallQueueMXBean` and `MetricsSource`, delegating through a weak reference and incrementing `revisionNumber` each time the active queue changes.

## Control flow

Producers use the `Schedulable` priority level. `add()` tries the requested queue and lower-priority queues, throwing `CallQueueOverflowException.DISCONNECT` only when the lowest-priority queue overflows and `KEEPALIVE` otherwise. `put()` tries all but the last queue and blocks on the last when necessary. `offer()` targets only the requested queue. Successful inserts release one semaphore permit.

Consumers acquire a semaphore permit before removing. `removeNextElement()` asks the multiplexer for a starting queue, polls it, and if empty scans all queues until it removes an element. This preserves the invariant that each acquired permit corresponds to one removed item despite races among consumers.

## State and persistence behavior

State is runtime-only: subqueue objects, semaphore permits, multiplexer, overflow counters, and metrics proxy delegate. `size()` reports semaphore permits, not a locked sum of subqueue sizes. No queue contents are persisted.

## Dependencies and integration points

The queue integrates with `CallQueueManager`, `Schedulable`, `RpcMultiplexer`, `WeightedRoundRobinMultiplexer`, JMX via `MBeans`, and Metrics2 via `DefaultMetricsSystem`. Overflow exceptions inform RPC connection behavior.

## Risks and test signals

Consistency is deliberately weak for `poll()`, `peek()`, and metrics snapshots. `drainTo()` drains permits first and restores unused permits; tests should verify no permit leaks under partial drains. `iterator()` is intentionally unimplemented. Useful tests cover capacity distribution, overflow behavior by priority, semaphore/subqueue synchronization under concurrency, multiplexer fairness, metrics revision changes, and weak-reference proxy behavior.
