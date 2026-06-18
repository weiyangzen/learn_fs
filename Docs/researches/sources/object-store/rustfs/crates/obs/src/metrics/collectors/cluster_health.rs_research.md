# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_health.rs

Purpose: reports cluster drive health counts: offline, online, and total drives.

Important APIs/types: `ClusterHealthStats` has three `u64` fields. `collect_cluster_health_metrics` maps those fields to `HEALTH_DRIVES_OFFLINE_COUNT_MD`, `HEALTH_DRIVES_ONLINE_COUNT_MD`, and `HEALTH_DRIVES_COUNT_MD`.

Control flow: fixed three-metric vector, no labels, direct conversion to `f64`.

State/persistence: no internal state. Upstream collection decides whether a drive is online/offline and computes totals.

Dependencies/integration: depends on `PrometheusMetric` and `schema::cluster_health`. The scheduler combines it with base cluster capacity metrics in the same cluster task.

Risks: caller must ensure `offline + online` equals `drives_count` if dashboards assume that invariant. Defaults produce zero-valued metrics, which can look like an empty healthy cluster if emitted before storage is initialized.

Test signals: tests assert three metrics, non-default offline/online values, and default zero/no-label behavior.
