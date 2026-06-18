# sources/object-store/rustfs/crates/common/src/metrics.rs

## Purpose
Central scanner and lifecycle metrics implementation for `rustfs-common`. It owns the process-wide `GLOBAL_METRICS`, records lifetime and last-minute scanner activity, tracks active scan paths and cycle state, emits selected `metrics` crate counters/histograms, and serializes report structs consumed by observability/admin layers.

## Important APIs, types, and functions
Key enums are `Metric`, `IlmAction`, `ScannerWorkSource`, and `ScanCyclePartialReason`. `Metrics` exposes synchronous recorders (`log`, `time`, `time_size`, `time_n`, `time_ilm`, `inc_time`), scanner-specific recorders for yield/throttle/ILM/transition/checkpoint/source work, async cycle/path accessors, and `report() -> ScannerMetricsReport`. `CurrentCycle::marshal/unmarshal` persists cycle metadata with `rmp_serde`. `current_path_updater` and `CloseDiskGuard` provide async callbacks for per-disk path tracking.

## Control flow
Callers either obtain `global_metrics()` or create a local `Metrics`. Operation timing APIs capture `SystemTime::now()` and return closures that update atomics and last-minute latency when invoked. Scanner cycles call `start_scan_cycle_work`, accumulate global counters during work, then `finish_scan_cycle_work` computes saturating deltas and stores last-cycle snapshots. `report()` gathers async cycle/path state, atomic counters, scanner pressure, maintenance-control status, lifetime maps, and last-minute maps into one serializable snapshot.

## State and persistence behavior
State is in memory: `AtomicU64`/`AtomicU8`/`AtomicBool` counters, `std::sync::Mutex` maps/options for short critical sections, and `tokio::sync::RwLock` maps for async path/cycle state. Only `CurrentCycle` has explicit binary marshal/unmarshal support. Ordering is mostly relaxed because these are telemetry counters, so report readers can observe mixed snapshots. `LockedLastMinuteLatency` intentionally clones into independent mutex-protected latency slots to avoid aliasing metrics.

## Dependencies and integration points
Depends on `crate::heal_channel::HealScanMode`, `crate::last_minute`, global init time, `chrono`, `serde`, `rmp_serde`, `tokio`, and the `metrics` facade. Scanner lifecycle, healing, replication, usage, and ILM code are expected to call the specific recorders. Observability exporters consume `ScannerMetricsReport` fields and OpenTelemetry metric names such as `rustfs_scanner_cycles_total`.

## Risks and edge cases
Relaxed atomics are appropriate for telemetry but not transactionally consistent. `current_path_updater` inserts the disk asynchronously with `tokio::spawn`, so very early reads can miss a newly registered path. `CloseDiskGuard::drop` silently skips cleanup without a Tokio runtime. `time_n` uses the original start time for all returned closures, which is correct for batch timing but surprising if reused. String labels and enum numeric indexes are compatibility-sensitive because reports expose both names and codes.

## Test signals
The module has broad Tokio/unit tests covering active path age, queue state, pacing pressure, checkpoint lifecycle, source-work accounting, lifecycle expiry/transition splits, transition queue snapshots, maintenance-control derivation, current/last cycle deltas, scan result labels, throttle config sanitization, cycle config, yield/throttle counters, and global metric-to-source mapping.
