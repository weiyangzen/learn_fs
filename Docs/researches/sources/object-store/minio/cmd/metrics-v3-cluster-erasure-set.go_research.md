# sources/object-store/minio/cmd/metrics-v3-cluster-erasure-set.go

Purpose: Exposes v3 erasure-set health, quorum, tolerance, and drive counts at cluster scope.

Important APIs/types/functions: Defines metric names for overall write quorum, overall health, per-set read/write quorum, online/healing drives, health, read/write tolerance, and read/write health. Labels are `pool_id` and `set_id`. `b2f` converts booleans to Prometheus numeric values. `loadClusterErasureSetMetrics` populates all values.

Control flow: The loader obtains cached `HealthResult` from `c.esetHealthResult`, sets overall write quorum and overall health, then iterates each `ESHealth` record. It emits per-pool/set quorum and drive gauges, converts set health to 1/0, computes read tolerance as healthy drives minus read quorum, and write tolerance as healthy plus healing drives minus write quorum. Negative tolerance flips the corresponding health gauge to 0.

State and persistence behavior: Stateless over cached health state. Values are live health snapshots refreshed through `metricsCache` with last-good behavior.

Dependencies and integration points: Depends on object-layer health via `newESetHealthResultCache`, `HealthResult.ESHealth`, and v3 metric descriptors. These metrics integrate with cluster health dashboards and alerting.

Risks: The loader ignores the cache error return, so zero-value health can be emitted if the cache cannot load and has no last-good value. Tolerance calculations are simple and depend on accurate `HealthyDrives`, `HealingDrives`, and quorum fields.

Test signals: No direct tests in this subset.
