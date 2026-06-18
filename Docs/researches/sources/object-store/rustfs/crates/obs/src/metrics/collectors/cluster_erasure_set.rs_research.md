# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_erasure_set.rs

Purpose: converts per-erasure-set topology, quorum, drive, tolerance, and health snapshots into labeled Prometheus gauges.

Important APIs/types: `ErasureSetStats` carries `pool_id`, `set_id`, set size, parity/data shards, read/write quorum, online/healing drive counts, health, read/write tolerance, and read/write health. `collect_erasure_set_metrics(&[ErasureSetStats])` emits metrics labeled by `pool_id` and `set_id`.

Control flow: preallocates `stats.len() * 12`, iterates each set, converts IDs to strings once, and pushes twelve gauge metrics using descriptors from `schema::cluster_erasure_set`. Labels are cloned across each metric to keep series distinguishable by pool and set.

State/persistence: stateless. The collector does not compute quorum or health; it trusts upstream `stats_collector::collect_erasure_set_stats`.

Dependencies/integration: used by the scheduler's supplementary cluster task. Descriptor label constants `POOL_ID_L` and `SET_ID_L` are imported from schema, reducing drift between schema declarations and emitted labels.

Risks: health fields are encoded as `u8` with comments saying 1 healthy and 0 unhealthy; no validation prevents other values. High pool/set counts increase series count linearly. Schema contains overall erasure-set descriptors that this collector does not emit, so future overall metrics need separate wiring.

Test signals: tests cover one-set output length of twelve, descriptor name/value checks for size and health, `report_metrics` compatibility, and empty-slice behavior.
