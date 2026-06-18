# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster.rs

Purpose: defines base cluster aggregate metric descriptors for capacity and object/bucket counts.

Important APIs/types: eight gauge descriptors: raw total capacity, usable total capacity, used bytes, free bytes, stale capacity drives, missing capacity drives, objects total, and buckets total.

Control flow: each `LazyLock` calls `new_gauge_md` with either `MetricName::Custom(...)` for capacity/count names and no labels, using `subsystems::CLUSTER_BASE_PATH`.

State/persistence: lazy descriptor initialization only.

Dependencies/integration: consumed by `collectors/cluster.rs`, then reported by the scheduler cluster task.

Risks: descriptors use custom metric names rather than dedicated enum variants for these aggregate names, so string stability is critical. All metrics are gauges; object and bucket totals are current snapshots, not monotonic counters. No labels means these must represent whole-cluster values.

Test signals: cluster collector tests validate descriptor-derived names and values for representative metrics.
