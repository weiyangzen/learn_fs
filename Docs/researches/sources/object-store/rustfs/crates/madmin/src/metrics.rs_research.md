# sources/object-store/rustfs/crates/madmin/src/metrics.rs

Purpose: defines admin metrics wire models and aggregation logic for disks, scanner, OS, RPC, network, memory, batch jobs, site resync, and realtime rollups.

Important APIs/types/functions: `TimedAction::merge` adds count/time/bytes. `DiskMetric::merge`, `OsMetrics::merge`, `NetMetrics::merge`, `RPCMetrics::merge`, `ScannerMetrics::merge`, `BatchJobMetrics::merge`, `SiteResyncMetrics::merge`, and `RealtimeMetrics::merge` aggregate node samples. Scanner-specific snapshots model cycle progress, partial-cycle sources, pacing pressure, lifecycle transition queues, maintenance control, scan checkpoint state, and source work. `Metrics` holds optional category metrics and delegates merges.

Control flow: merge methods combine distributed samples. Timestamps choose freshest metadata for collected times, last ping/connect, site resync, and scanner status fields. Counters mostly add, many scanner counters use `saturating_add`; pressure and maintenance choose dominant state via priority helpers, then sort per-source vectors for deterministic output. `RealtimeMetrics` replaces per-host/per-disk entries while merging aggregated metrics.

State and persistence: no storage, but the structs are state snapshots. Aggregation mutates in-memory accumulators and preserves API field names with serde renames/defaults.

Dependencies/integration: depends on `chrono`, serde, `HashMap`, and `health::MemInfo`. `info_commands::DiskMetrics` reuses `TimedAction`; admin metric endpoints can stream host/disk entries into `RealtimeMetrics`.

Risks: integer addition in some merge paths is non-saturating (`RPCMetrics`, `NetMetrics`, maps), so extreme cumulative values could overflow in debug or wrap in release. Merge semantics are not uniform: some fields sum, some max, some replace with newest, and `BatchJobMetrics` overwrites jobs by ID. `Metrics::merge` currently ignores `mem` and `cpu`, so those categories are not aggregated.

Test signals: tests exercise scanner merge behavior for partial-cycle sources, pause pressure, lifecycle transition status, maintenance-control priority, and distributed status fields. Other merge paths rely mainly on compile/serde coverage.
