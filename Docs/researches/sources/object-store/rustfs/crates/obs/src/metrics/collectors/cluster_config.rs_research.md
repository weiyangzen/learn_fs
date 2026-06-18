# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_config.rs

Purpose: exposes storage class parity settings as Prometheus gauges, specifically reduced redundancy storage parity and standard storage parity.

Important APIs/types: `ClusterConfigStats` holds `rrs_parity` and `standard_parity` as `u32`. `collect_cluster_config_metrics` returns two metrics from `CONFIG_RRS_PARITY_MD` and `CONFIG_STANDARD_PARITY_MD`.

Control flow: fixed vector construction with direct field-to-descriptor mapping and no labels. The file is marked `#![allow(dead_code)]`, reflecting that this collector may be available before all runtime sources are wired in every build path.

State/persistence: no persistence or side effects. Runtime configuration is gathered elsewhere, then materialized as this DTO.

Dependencies/integration: depends on `PrometheusMetric` and `schema::cluster_config`. The supplementary cluster metrics scheduler task calls `collect_cluster_config_stats().await`, then emits these metrics only when that optional source returns `Some`.

Risks: zero is both the `Default` value and a possible placeholder for unavailable configuration, so absent data must be represented by not emitting metrics rather than passing defaults where possible. Gauge semantics are appropriate, but descriptor names must remain stable for dashboards.

Test signals: tests verify a two-metric output, expected values for non-default parity, and zero/default no-label behavior.
