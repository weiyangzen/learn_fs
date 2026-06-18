# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeMetrics.java

## Purpose
`SCMNodeMetrics` is the Hadoop metrics source for SCM node manager counters and gauges. It exposes heartbeat/report processing counters, pending-container allocation counters, and dynamic gauges derived from `NodeManagerMXBean`.

## Important APIs, Types, And Functions
`create` registers the metrics source under `SCMNodeMetrics` in `DefaultMetricsSystem`; `unRegister` removes it. Package-private incrementers update heartbeat, node-report, command-queue-report, pending-container, and skipped-full-node-allocation counters. `getMetrics` builds node-state cross-product gauges, all-node count, non-writable and volume-failure gauges, and storage capacity/usage gauges. `diskMetricDescription` creates human-readable descriptions for generated storage metrics.

## Control Flow
Metrics snapshots call back into the supplied `NodeManagerMXBean` for current `getNodeCount`, `getNodeInfo`, and `getNodeStatistics` maps. For each operational/health combination it camelizes a gauge name and increments an aggregate `AllNodes` gauge. Optional map keys such as `NonWritableNodes` and `VolumeFailures` are checked before adding gauges. Remaining storage entries are emitted with descriptions inferred from their names.

## State And Persistence Behavior
The class keeps Hadoop `MutableCounterLong` counters in memory. Gauges are not stored; they are recomputed on collection. Registration state lives in the process metrics system and must be explicitly unregistered to prevent duplicate sources in tests or restarted services.

## Dependencies And Integration Points
It depends on Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, `Interns`, and the `NodeManagerMXBean` contract. `SCMNodeManager` creates and updates it, and observability systems scrape the generated metrics.

## Risks And Edge Cases
Gauge names are generated from map keys, so changing `SCMNodeManager` labels can break dashboards. `getMetrics` parses `NonWritableNodes` and `VolumeFailures` from strings, so malformed values from the MXBean would throw during metrics collection. Missing optional keys are tolerated. The `textMetric` field appears test-like and not functionally important.

## Test Signals
Tests should verify metrics registration/unregistration, counter increments, generated cross-product gauges for all node states, storage gauge description mapping, and behavior when optional node-statistics keys are absent or present.
