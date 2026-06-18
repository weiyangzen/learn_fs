# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/MutableMinMax.java

## Purpose

`MutableMinMax` is a custom metrics2 `MutableMetric` tracking interval minimum and maximum values for a named metric.

## APIs and control flow

Construction derives metrics names from the base name, description, and value name, then registers placeholder gauges in the supplied registry for annotation compatibility. `add(value)` updates the current interval min/max and marks the metric changed. `snapshot(builder, all)` emits either current interval or previous interval values, then rolls the current interval into `prevMinMax`, resets the interval, and clears the changed flag when appropriate.

## State, dependencies, and integration

State is two `SampleStat.MinMax` instances and two `MetricsInfo` descriptors. The class is synchronized around mutation and snapshotting. It depends on Commons `StringUtils`, HDDS annotations, and Hadoop metrics2. `PerformanceMetrics` uses it beside stats and quantiles.

## Risks and test signals

Description strings concatenate `"description" + "in"` without an inserted space. Empty intervals use previous values when unchanged, which is intentional but should be understood by dashboards. Tests should cover min/max rollovers, `all=true` snapshots, no-data behavior, and thread-safe add/snapshot interaction.
