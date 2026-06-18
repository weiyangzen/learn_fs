# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/MetricUtil.java

## Purpose

`MetricUtil` contains helper methods for latency capture and quantile lifecycle management in Ozone metrics code.

## APIs and control flow

Four `captureLatencyNs` overloads wrap checked suppliers or runnables, record `Time.monotonicNowNanos()` before execution, and add or pass elapsed nanoseconds in a `finally` block so failures are still measured. `createQuantiles` validates that the interval array is non-null, returns an empty list for zero intervals, and registers one `MutableQuantiles` per interval using a `<name><interval>s` naming convention. `stop` overloads safely stop non-null quantile instances.

## State, dependencies, and integration

The class is stateless. It depends on Hadoop metrics2, Hadoop `Time`, Ratis checked functional interfaces, and Java collections/consumers. It integrates with metrics sources and `PerformanceMetrics`.

## Risks and test signals

Latency capture changes exception timing but preserves exception propagation. Quantile names can collide if callers reuse the same base name and interval. Tests should cover successful and failing blocks, null and empty intervals, quantile registration names, and stopping nullable collections.
