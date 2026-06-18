# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_erasure_set.rs

Purpose: defines descriptors and labels for erasure set topology, quorum, drive count, tolerance, and health metrics.

Important APIs/types: label constants `POOL_ID_L` and `SET_ID_L`; descriptors for set size, parity, data shards, overall write quorum, overall health, read/write quorum, online/healing drive count, health, read/write tolerance, and read/write health.

Control flow: descriptors are `LazyLock<MetricDescriptor>` values built with `new_gauge_md`. Most descriptors include `[POOL_ID_L, SET_ID_L]`; overall descriptors are unlabeled.

State/persistence: lazy immutable descriptor initialization only.

Dependencies/integration: per-set descriptors are used by `collectors/cluster_erasure_set.rs`. Overall descriptors are defined but not emitted by that collector in the reviewed code.

Risks: comment for `SET_ID_L` says "pool ID", a documentation copy/paste issue. Overall descriptors without collector wiring can confuse maintainers expecting all schema entries to be emitted. Health values are numeric gauges, so conventions must be documented.

Test signals: erasure set collector tests validate size/health descriptors and label-producing collection.
