# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeMetrics.java

## Purpose
Metrics source for Merkle tree persistence, read/diff failures, diff outcomes, identified repair items, and latency rates.

## Important APIs, Types, And Functions
Static APIs `create` and `unregister`; increment methods for write/read/diff failures, no-repair/repair diffs, missing/corrupt/diverged counts; getters for `MutableRate` latency metrics and selected counters.

## Control Flow
`create` unregisters any existing source of the same name before registering a fresh `ContainerMerkleTreeMetrics`. Manager code increments counters and records latencies through `MetricUtil.captureLatencyNs`.

## State And Persistence
Metrics live in Hadoop `DefaultMetricsSystem`; counters/rates are mutable fields injected by metrics registration.

## Dependencies And Integration Points
Used by `ContainerChecksumTreeManager` and exposed through Hadoop metrics/JMX sinks.

## Risks
Unregistering an existing source on create can disturb another active manager if multiple managers are created in the same JVM. Some counters have getters while others do not.

## Test Signals
Signals include metrics source registration/unregistration, incremented counters after simulated read/write/diff failures, latency samples, and no duplicate source registration errors.
