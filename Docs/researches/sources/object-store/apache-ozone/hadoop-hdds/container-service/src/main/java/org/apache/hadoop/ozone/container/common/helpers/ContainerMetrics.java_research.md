# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerMetrics.java

## Purpose
Metrics source for storage container datanode operations, bytes, latencies, closed-container bytes, delete failures, read state-machine stats, and reconciliation outcomes.

## Important APIs, Types, And Functions
Static APIs `create(conf)` and `remove`; instance methods increment operation counts, latencies, bytes, closed-container bytes, delete failure counters, force deletes, read-state-machine counters, and reconciliation counters. It implements `Closeable` to stop quantiles.

## Control Flow
Construction creates per-`ContainerProtos.Type` counters/rates and optional quantiles based on configured percentile intervals. Runtime handlers increment metrics by operation type and add latency samples.

## State And Persistence
Metrics are registered in `DefaultMetricsSystem`; per-type metric objects live in enum maps and a metrics registry. Quantiles have background resources stopped by `close`.

## Dependencies And Integration Points
Depends on HDDS metrics percentile config, Hadoop metrics registry, container protobuf operation types, and `MetricUtil`.

## Risks
The constructor reuses the same `MutableQuantiles[]` reference for every operation type, so all map entries share the final array contents; this may be unintended and can mix quantile state. Callers must close to stop quantile resources and remove to unregister.

## Test Signals
Signals include per-operation counters/bytes/latencies, configured quantile emission, closed-container byte tracking, delete failure counters, reconciliation counters, and no leaked quantile threads after close.
