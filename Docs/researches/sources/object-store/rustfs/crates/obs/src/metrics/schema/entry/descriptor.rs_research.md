# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/descriptor.rs

## Purpose
Defines `MetricDescriptor`, the common metadata object used by all schema modules to describe exported Prometheus metrics.

## Important APIs, Types, and Functions
`MetricDescriptor` stores `name`, `metric_type`, `help`, `variable_labels`, `namespace`, and `subsystem`. `MetricDescriptor::new()` constructs descriptors. `get_full_metric_name()` returns Prometheus-style `<namespace>_<subsystem>_<name>`. `has_label()` and `get_label_set()` lazily build and query a `HashSet<String>` from `variable_labels`.

## Control Flow
Construction is direct. Full-name generation calls `MetricNamespace::as_str()`, `MetricSubsystem::as_str()`, and `MetricName::as_str()`. Label lookup initializes `label_set` only once, then reuses it.

## State and Persistence
The only mutable state is the private `label_set` cache, which requires `&mut self` to populate. There is no persistence. Because descriptors are generally held in `LazyLock`, callers needing `has_label()` must account for mutable access constraints.

## Dependencies and Integration Points
Used by all schema descriptor modules and by collectors through `PrometheusMetric::from_descriptor`. It depends on the schema entry enums for names, namespaces, subsystems, and metric types.

## Risks
`get_full_metric_name()` always includes namespace and subsystem, so empty or malformed custom subsystem paths can create unexpected names. `MetricSubsystem::as_str()` allocates a `String`; repeated name construction can allocate. The mutable label cache may be awkward for static descriptors if more validation code is added.

## Test Signals
Tests assert full metric names for built-in and custom subsystems, including that metric type prefixes are not inserted. There is no test for `has_label()` caching behavior.
