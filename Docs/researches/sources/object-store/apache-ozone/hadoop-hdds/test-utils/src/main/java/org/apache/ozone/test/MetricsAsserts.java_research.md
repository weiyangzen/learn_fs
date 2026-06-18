# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/MetricsAsserts.java

Purpose: `MetricsAsserts` provides assertion and extraction helpers for Hadoop Metrics2 sources. It lets tests mock metrics collectors, invoke a `MetricsSource`, and verify gauges, counters, tags, and quantile gauges by metric name.

Important APIs and types: Key APIs include `mockMetricsSystem`, `mockMetricsRecordBuilder`, `getMetrics`, overloaded `assertGauge` and `assertCounter`, `getIntGauge`, `getLongGauge`, `getDoubleGauge`, `getFloatGauge`, `getLongCounter`, `getStringMetric`, `assertCounterGt`, `assertGaugeGt`, `assertGaugeGte`, `assertQuantileGauges`, `assertInverseQuantileGauges`, `assertTag`, and `getStringTag`. It uses `MetricsCollector`, `MetricsRecordBuilder`, `MetricsSource`, `DefaultMetricsSystem`, `MutableQuantiles`, Mockito captors/matchers, and AssertJ offsets.

Control flow: `mockMetricsRecordBuilder` returns a Mockito builder that chains most metric methods to itself and returns the collector for `parent` or `endRecord`. `getMetrics` invokes a source with the mock collector. Getter methods verify the builder received exactly one matching metric call by name and return the captured value. Quantile helpers verify percentile gauge names for the default quantiles.

State and persistence behavior: No persistence. `mockMetricsSystem` mutates the global `DefaultMetricsSystem` singleton. Assertions inspect Mockito invocation history and captured values.

Dependencies and integration points: Used throughout Ozone metrics tests to verify Metrics2 source output without starting a real metrics sink. It bridges Hadoop metric names created through `Interns.info` with Mockito name matchers.

Risks: `atLeast(0)` permits missing invocations until `checkCaptured` catches zero captures. Global metrics system replacement can affect tests running in parallel. Quantile naming is tied to Hadoop's default `MutableQuantiles` percentiles and suffix conventions.

Test signals: Exact metric values, greater-than comparisons, single-capture enforcement, tag values, and presence of all expected quantile percentile gauges.
