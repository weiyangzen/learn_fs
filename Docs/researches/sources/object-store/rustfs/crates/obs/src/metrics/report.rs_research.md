# sources/object-store/rustfs/crates/obs/src/metrics/report.rs

Purpose: defines the intermediate `PrometheusMetric` representation and the `report_metrics` bridge that registers/describes metrics through the `metrics` crate macros.

Important APIs/types: `PrometheusMetric` with name/type/help/labels/value, constructors `new`, `new_owned`, `from_descriptor`, and label builders `with_label`, `with_label_owned`, `with_labels`. `report_metrics(&[PrometheusMetric])` emits to the global metrics recorder. Static `NAME_CACHE` and `HELP_CACHE` intern dynamic names/help as leaked `'static` strings.

Control flow: `report_metrics` interns name/help, describes the metric based on `MetricType`, converts labels to owned `(String,String)` pairs, then records counters using `absolute(metric.value as u64)`, gauges with `set`, and histograms with `record`.

State/persistence: process-local caches store interned strings forever. This avoids lifetime issues for metrics macros but can grow if metric names/help are unbounded.

Dependencies/integration: all collectors return `PrometheusMetric`; scheduler calls `report_metrics` after each collection batch.

Risks: counter values are cast to `u64`, truncating floats and wrapping/saturating semantics depending on Rust cast behavior for invalid values; callers should supply non-negative whole counter values. Dynamic metric names can leak memory through intern caches. Histogram handling records values rather than explicit bucket counts, so distribution collectors must align with `metrics` crate semantics.

Test signals: test verifies `from_descriptor` generates full Prometheus names for counter/gauge/histogram descriptor cases.
