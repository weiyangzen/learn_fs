# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_drive.rs

Purpose: emits detailed per-drive telemetry, aggregate drive counts, and process disk I/O metrics.

Important APIs/types: `DriveDetailedStats`, `DriveCountStats`, `ProcessDiskStats`, `collect_drive_detailed_metrics`, `collect_drive_count_metrics`, and `collect_process_disk_metrics`. Detailed stats include capacity, observation state/age, inodes, errors, waiting I/O, latency, health, read/write rates, awaits, and utilization.

Control flow: detailed collection uses an inner `push_drive_metric` helper to attach `drive` and `server` labels. It emits 23 metrics per drive, including three one-hot `capacity_observation_state` samples for `live`, `stale`, and `missing`. Drive count emits three unlabeled metrics. Process disk emits one metric twice with `direction=read/write` plus optional process labels.

State/persistence: stateless conversion. Observation freshness and disk I/O rates are computed upstream.

Dependencies/integration: the scheduler node/disk task combines detailed drive, aggregate count, and simpler node disk metrics. The system monitoring task emits process disk I/O as part of process labels.

Risks: drive paths/server labels drive series cardinality and churn. The capacity observation state is a caller-provided `&'static str`; unrecognized values result in all three known states being 0. Process disk metric uses one descriptor with a direction label.

Test signals: tests assert 23 detailed metrics for one drive, exact total bytes, and three drive count metrics with offline value. Process disk behavior is indirectly used by scheduler/system tests.
