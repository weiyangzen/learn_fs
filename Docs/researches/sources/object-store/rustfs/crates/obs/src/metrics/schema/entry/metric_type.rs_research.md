# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/metric_type.rs

## Purpose
Defines the small enum representing metric kind: counter, gauge, or histogram.

## Important APIs, Types, and Functions
`MetricType` has variants `Counter`, `Gauge`, and `Histogram`. `as_str()` returns plain text type names. `as_prom()` returns type-specific prefixes with trailing dots, although comments indicate this is an approximation for Prometheus client concepts.

## Control Flow
Both methods are simple matches. The main schema factories embed `MetricType` values into `MetricDescriptor`.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Used by descriptor factories, descriptors, and downstream conversion to `PrometheusMetric`. Actual exposition type behavior depends on collector/report code, not only this enum.

## Risks
`as_prom()` returns strings like `counter.` and is marked dead code; if used later, the trailing dot contract needs validation. Histograms are not currently wired by the public schema modules in this subset except through the factory test, and some histogram-like descriptors are defined as counters or gauges.

## Test Signals
No tests in this file. The `entry/mod.rs` histogram factory test checks that a histogram descriptor stores `MetricType::Histogram`.
