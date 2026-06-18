# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/PerformanceMetrics.java

## Purpose

`PerformanceMetrics` groups a `MutableStat`, optional interval quantiles, and `MutableMinMax` under one metric name so callers can update and snapshot a full latency/performance metric consistently.

## APIs and control flow

`initializeMetrics(source, registry, sampleName, valueName, intervals)` delegates reflection-based initialization to `PerformanceMetricsInitializer` and wraps `IllegalAccessException` in a runtime exception. The constructor registers the stat, quantiles, and min/max metric. `add(value)` updates all three families. `snapshot(recordBuilder, all)` emits all component snapshots. `close()` stops quantile threads/resources.

## State, dependencies, and integration

State is the three metrics components. Dependencies are Hadoop metrics2 and local `MetricUtil`/`MutableMinMax`. It integrates with metrics sources that declare `PerformanceMetrics` fields annotated with `@Metric`.

## Risks and test signals

Each quantile interval consumes additional resources and must be stopped. Reflection initialization mutates private fields. Tests should cover annotated-field initialization, add/snapshot propagation, close idempotence expectations, and behavior when no intervals are supplied.
