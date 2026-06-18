<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerMetrics.java

## Purpose

`ReplicationManagerMetrics` is the Hadoop metrics source for SCM ReplicationManager. It exposes inflight add/delete gauges, queue depths, lifecycle and health-state gauges from `ReplicationManagerReport`, and counters/rates for Ratis and EC replication, deletion, reconstruction, partial replication, skipped inflight operations, and deferred commands.

## Important APIs, Types, and Functions

The class implements `MetricsSource`. Key APIs are `create`, `unRegister`, `getMetrics`, the `incr*` counter methods, `addReplicationTime`, `addDeletionTime`, and gauge getters such as `getInflightReplication`, `getEcReplication`, and `getPendingReplicationLimitReachedTotal`. It builds `MetricsInfo` maps for every `LifeCycleState` and `ContainerHealthState`.

## Control Flow

`create` registers a singleton source with `DefaultMetricsSystem`. `getMetrics` constructs a metrics record, reads live queue and pending-op state from `ReplicationManager`, snapshots counters, and publishes dynamic report gauges. Mutator methods are called by replication command scheduling, timeout handling, pending-op completion, EC reconstruction paths, and throttling paths.

## State and Persistence Behavior

State is in-memory metrics registry state: `MutableCounterLong` and `MutableRate` fields plus live references to `ReplicationManager`. It does not persist values across SCM restart. Gauge values are derived at collection time from pending ops, queues, and the latest replication-manager report.

## Dependencies and Integration Points

It integrates with Hadoop metrics2, `ReplicationManager`, `ContainerReplicaPendingOps`, `ReplicationQueue`, `ReplicationManagerReport`, `ContainerHealthState`, `LifeCycleState`, and replication types. Dashboards and tests consume the metric names, so names are effectively a monitoring contract.

## Risks and Edge Cases

Metrics are only as accurate as the callers incrementing them; missing increments silently hide work. Dynamic lifecycle/health metrics expand if enums expand, which is useful but may surprise dashboards. The `getMetrics` body snapshots `ecReplicasDeletedTotal` twice and omits several byte/rate snapshots, which is a possible observability gap if not intentional.

## Test Signals

Useful tests assert registration idempotence, counter increments after command scheduling and timeout paths, inflight gauges matching pending-op counts split by Ratis/EC, queue gauges matching `ReplicationQueue`, lifecycle and health gauges matching sampled reports, and unregister cleanup from the metrics system.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerMetrics.java -->
