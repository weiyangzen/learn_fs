# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_health.rs

Purpose: defines cluster drive health count descriptors.

Important APIs/types: `HEALTH_DRIVES_OFFLINE_COUNT_MD`, `HEALTH_DRIVES_ONLINE_COUNT_MD`, and `HEALTH_DRIVES_COUNT_MD`, all gauges with no labels under `subsystems::CLUSTER_HEALTH`.

Control flow: lazy descriptor construction through `new_gauge_md` and `MetricName` enum variants for offline, online, and total drive counts.

State/persistence: lazy immutable descriptors only.

Dependencies/integration: used by `collectors/cluster_health.rs`; scheduler emits these with base cluster metrics.

Risks: all metrics are unlabeled cluster-wide snapshots. Consumers may infer total from offline+online, but schema exposes total separately and upstream must keep values consistent.

Test signals: cluster health collector tests validate count and representative values, plus default no-label zero behavior.
