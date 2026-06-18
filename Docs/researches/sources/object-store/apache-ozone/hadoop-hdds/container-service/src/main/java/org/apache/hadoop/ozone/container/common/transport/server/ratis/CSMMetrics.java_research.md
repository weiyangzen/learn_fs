<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/CSMMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/CSMMetrics.java

## Purpose

`CSMMetrics` registers Hadoop metrics for a single Ratis container state machine and records operation counts, failure counts, byte counts, cache behavior, queueing, and latency. The complete 265-line file was read.

## Important APIs, Types, and Functions

The class is annotated with `@Metrics` and is created via `create(RaftGroupId)`. Public methods increment counters for write/query/read/apply operations and failures, bytes written/committed, start-transaction verification failures, data cache hits/misses/evictions, pending apply transactions, and latency samples. `getRaftGroupId()` is exported as a metric. `unRegister()` removes the metrics source.

## Control Flow

Construction creates a `MetricsRegistry` and allocates per-`ContainerProtos.Type` `MutableRate` instances for latency and queueing delay. `create` registers a source named `CSMMetrics` plus the raft group id. State-machine code calls the increment/record methods at transaction start, write state-machine data completion, apply completion, read fallback, and failure paths.

## State and Persistence Behavior

All state is in memory inside Hadoop metrics objects. No durable persistence occurs. The source is scoped by raft group id and should be unregistered when a state machine closes.

## Dependencies and Integration Points

It integrates with `DefaultMetricsSystem`, `MetricsRegistry`, `MutableCounterLong`, `MutableRate`, Ratis `RaftGroupId`, and `ContainerStateMachine`.

## Risks and Edge Cases

Metrics source names include `gid.toString()`, so duplicate registration for the same group would conflict. `pendingApplyTransactions` is decremented by `incr(-1)`, which assumes counter implementations allow negative increments. Per-command enum maps allocate rates for all command types, including rarely used ones.

## Test Signals

Tests should verify registration/unregistration names, counter increments for success and failure paths, per-type latency/queue rates, cache hit/miss/eviction counters, and pending-apply increment/decrement balance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/CSMMetrics.java -->
