# sources/user-network-fs/gcsfuse/metrics/otel_metrics_test.go

## Purpose

Auto-generated Go test suite for the `metrics` package's OpenTelemetry implementation. It verifies that `NewOTelMetrics` creates usable instruments and that generated metric methods emit the expected metric names, attributes, aggregation behavior, and histogram units.

## Important APIs, Types, and Functions

Defines `metricValueMap`, `metricHistogramMap`, `setupOTel`, `gatherNonZeroCounterMetrics`, and `gatherHistogramMetrics`. Tests exercise methods on `*otelMetrics` including buffered read, file cache, filesystem ops/error/latency, streaming write fallback, GCS read/download/request/retry, metadata cache, read block sizes, and test up/down counters.

## Control Flow

Each test installs a manual OpenTelemetry reader, calls metric methods, waits briefly, manually collects resource metrics, filters relevant `Sum[int64]` or `Histogram[int64]` data points, encodes attributes with `attribute.DefaultEncoder`, and compares against expected maps or histogram count/sum values. Large table-driven tests enumerate known operation, method, error, and attribute values.

## State and Persistence Behavior

The file mutates process-local OpenTelemetry global meter provider state and in-memory metric accumulators only. It writes no external files and sends no external telemetry.

## Dependencies and Integration Points

Depends on `testify`, OpenTelemetry global/provider/manual reader APIs, generated `otelMetrics`, and generated metric names/attribute keys. The file is auto-generated, so the stable integration point is the metric definition generator.

## Risks and Edge Cases

The 5 ms processing wait may become flaky if metrics become asynchronous. Zero-valued sums are filtered, so zero emission is indistinguishable from no emission. Histograms assert count and sum but not bucket boundaries. Global provider replacement could conflict with parallel package tests.

## Test Signals

Strong signals are missing metric names, mismatched encoded attribute sets, incorrect negative increment handling for monotonic counters vs up/down counters, and histogram sum mismatches for microsecond, millisecond, and raw size values.
