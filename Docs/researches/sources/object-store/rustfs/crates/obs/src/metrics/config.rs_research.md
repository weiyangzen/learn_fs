# sources/object-store/rustfs/crates/obs/src/metrics/config.rs

Purpose: centralizes public environment variable names and default intervals for metrics collection categories.

Important APIs/types: constants for default, cluster, bucket, node, resource, audit, notification, and bucket replication bandwidth intervals. Defaults are `Duration` values: 60s cluster/node, 300s bucket, 15s resource/audit/notification, and 30s replication bandwidth.

Control flow: constants only; parsing is implemented in `scheduler.rs`.

State/persistence: no state. Values are compile-time defaults used by runtime configuration.

Dependencies/integration: `scheduler.rs` imports these constants into `configured_metrics_runtime_config`, combines them with primary/legacy env var parsing, and exposes effective values in runtime snapshots.

Risks: the global `DEFAULT_METRICS_INTERVAL` is marked dead code but the env key is used as a fallback in scheduler parsing. Changing names breaks deployment configuration. Bucket default is intentionally longer due to cost and should not be casually reduced.

Test signals: no local tests; scheduler snapshot tests indirectly validate interval propagation when using fixed configs, and env parsing logic is concentrated in scheduler.
