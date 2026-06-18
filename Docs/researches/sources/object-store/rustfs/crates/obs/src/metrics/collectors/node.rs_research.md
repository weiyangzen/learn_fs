# sources/object-store/rustfs/crates/obs/src/metrics/collectors/node.rs

Purpose: emits per-node/per-disk capacity metrics for storage disks: total, used, and free bytes.

Important APIs/types: `DiskStats` contains `server`, `drive`, `total_bytes`, `used_bytes`, and `free_bytes`. `collect_node_metrics(&[DiskStats])` emits three metrics per disk.

Control flow: returns an empty vector for empty input. For each disk, clones server and drive labels as `Cow` values, then emits total/used/free descriptors with `server` and `drive` labels.

State/persistence: stateless conversion. Disk discovery and capacity observation happen in upstream stats collection.

Dependencies/integration: uses `schema::node_disk` descriptors. The node/disk scheduler task combines this output with detailed system drive metrics and aggregate drive count metrics.

Risks: label values include drive paths and server endpoints; changing formatting will create new Prometheus series. There is overlap with `system_drive.rs`, so dashboards should distinguish simple node disk capacity from richer system drive telemetry.

Test signals: tests cover two-disk output count, exact label/value matches, empty input, label presence on all metrics, and default DTO values.
