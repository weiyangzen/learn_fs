
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/FairCallQueueMXBean.java

## Purpose

This interface defines the JMX contract for `FairCallQueue` queue sizes, overflow counts, and delegate revision.

## Important APIs, types, and functions

`getQueueSizes()` returns per-priority subqueue sizes, `getOverflowedCalls()` returns per-priority overflow counters, and `getRevision()` reports how many times the metrics proxy has been pointed at a queue.

## Control flow

There is no local control flow. `FairCallQueue.MetricsProxy` implements the interface and delegates to the current queue if available.

## State and persistence behavior

The interface owns no state. Implementations expose in-memory snapshots only.

## Dependencies and integration points

It is registered by `FairCallQueue` through Hadoop `MBeans` and consumed by operators, metrics tooling, and tests.

## Risks and test signals

Tests should confirm empty arrays when no delegate exists, stable array lengths matching priority levels, and revision increments after delegate replacement.
