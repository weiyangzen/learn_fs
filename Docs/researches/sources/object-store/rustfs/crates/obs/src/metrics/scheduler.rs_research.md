# sources/object-store/rustfs/crates/obs/src/metrics/scheduler.rs

Purpose: initializes and supervises the background metrics runtime. It parses intervals, exposes runtime status/controller snapshots, and spawns asynchronous collection loops for cluster, bucket, node/disk, replication, audit, notification, background workflow, system/process, and internode network metrics.

Important APIs/types: `MetricsRuntimeServiceState`, cancellation/shutdown enums, interval/status/desired/controller snapshots, `MetricsRuntimeController`, `MetricsRuntimeConfig`, `init_metrics_runtime`, `init_metrics_collectors`, `metrics_runtime_status_snapshot`, and `metrics_runtime_controller_snapshot`. Replication bandwidth tombstone helpers manage zero emission for removed `(bucket,target_arn)` series.

Control flow: configuration parsing prioritizes primary env, legacy env, default env, legacy default, then hard-coded default. `init_metrics_runtime` captures config and spawns ten Tokio tasks. Each task uses `tokio::select!` between interval ticks and cancellation token. Collection tasks gather stats through `stats_collector` or external crates, convert through collectors, and call `report_metrics`. System monitoring uses deadlines to multiplex resource/system intervals on one loop.

State/persistence: no persistent files. Runtime state lives in spawned tasks, cancellation token status, process-local tombstone maps/sets, sysinfo `System`, and interned metric caches in `report.rs`.

Dependencies/integration: integrates with `rustfs_audit`, `rustfs_notify`, `rustfs_ecstore`, `rustfs_utils`, `tokio`, `tokio_util`, `sysinfo`, `tracing`, collectors, schema descriptors, and stats collection functions.

Risks: all tasks are spawned without handles, so cancellation is token-based only. First `tokio::time::interval` tick fires immediately, which is usually desired but can create startup load. Tombstone logic depends on monitor availability to avoid expiring/removing series during outages. GPU collector initialization happens during system intervals when feature-enabled. Large collector batches can block a task until collection/reporting completes.

Test signals: tests cover status disabled/running/stopping snapshots, controller reconciliation idempotence, deadline advancement including missed intervals, and replication bandwidth tombstone creation, zero metrics, expiry, live-key revival, and monitor-unavailable behavior.
