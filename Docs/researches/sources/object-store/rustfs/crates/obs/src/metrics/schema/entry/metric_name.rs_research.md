# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/metric_name.rs

## Purpose
Centralizes the metric-name vocabulary for RustFS observability. Every schema descriptor points at a `MetricName` variant or uses `MetricName::Custom` for ad hoc names.

## Important APIs, Types, and Functions
`MetricName` is a large enum covering generic counters, byte counters, latency metrics, API request metrics, audit/config/erasure/health/IAM/notification/usage/ILM/replication/scanner/system/process metrics, and `Custom(String)`. `MetricName::as_str()` maps each variant to the final metric-name suffix. `From<String>` and `From<&str>` create `Custom` names.

## Control Flow
The implementation is a single exhaustive `match` in `as_str()`. Descriptor factories call this indirectly through `MetricDescriptor::get_full_metric_name()`. Custom names bypass validation and are returned unchanged.

## State and Persistence
The enum stores no runtime metric values. `Custom(String)` carries caller-provided name state in descriptors. There is no persistence.

## Dependencies and Integration Points
Every schema module imports this enum. Collectors depend on the suffix strings remaining stable because full Prometheus names are composed from namespace, subsystem, and these suffixes.

## Risks
This file is a high-blast-radius naming contract. Typographical changes or duplicate-seeming suffixes can silently break dashboards and alert rules. `Custom` allows invalid Prometheus suffixes unless callers self-police. Some names preserve legacy terminology such as Go routines, and some type semantics are determined outside this file.

## Test Signals
No local tests cover the full mapping. Descriptor tests exercise a few names such as `ApiRequestsTotal` and `TtfbDistribution`. A generated snapshot test for all variant suffixes would be valuable.
