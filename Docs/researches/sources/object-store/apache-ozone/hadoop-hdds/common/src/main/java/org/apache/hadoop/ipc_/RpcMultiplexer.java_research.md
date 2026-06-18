
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/RpcMultiplexer.java

## Purpose

`RpcMultiplexer` is the strategy interface that chooses which `FairCallQueue` subqueue should be polled next.

## Important APIs, types, and functions

The single method `getAndAdvanceCurrentIndex()` returns the current queue index and may update internal state for the next call.

## Control flow

`FairCallQueue.removeNextElement()` calls the multiplexer after acquiring a semaphore permit. If the chosen queue is empty, `FairCallQueue` scans all queues to satisfy the permit.

## State and persistence behavior

The interface has no state. Implementations such as `WeightedRoundRobinMultiplexer` maintain runtime scheduling cursors.

## Dependencies and integration points

It integrates with `FairCallQueue` and configurable queue fairness policies.

## Risks and test signals

Implementations must return indexes within the configured queue range and be thread-safe enough for concurrent consumers. Tests should cover index bounds, fairness/weight behavior, and behavior when selected queues are empty.
