# sources/object-store/garage/src/rpc/system_metrics.rs

Purpose: OpenTelemetry observers for Garage system, disk, cluster health, and per-layout-node status.

Important APIs and types: `SystemMetrics` owns value observers for build info, replication factor, local disk availability/total, cluster healthy/available flags, node/partition counts, per-node connected status, and disconnected time. `SystemMetrics::new` registers instruments under `garage_system`.

Control flow: construction creates a one-second cached closure around `System::health` to avoid recomputing expensive partition health for every observer. Observers read `System::local_status`, `cluster_layout`, and `get_known_nodes`, attach role labels when available, and observe current values.

State and persistence: no persistence. The only mutable state is the short-lived `RwLock` health cache captured by observers. `System::cleanup` drops metrics to break reference cycles.

Dependencies and integration: depends on OpenTelemetry, `System`, `ClusterHealthStatus`, and Garage version helpers. Created during `System::new` and held in an `ArcSwapOption`.

Risks and test signals: observer closures capture `Arc<System>`, so cleanup is needed to avoid cycles. Labels include node IDs and role properties; cardinality grows with cluster size and role churn. Some comments note omitted hostname/address labels because OpenTelemetry aggregation would duplicate metrics. No direct tests.
