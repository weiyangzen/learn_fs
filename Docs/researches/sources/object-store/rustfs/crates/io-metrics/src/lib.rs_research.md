<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/lib.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/lib.rs

### Purpose
Acts as the public facade and metric-name implementation hub for `rustfs-io-metrics`. It re-exports submodules and defines many top-level `record_*` functions for S3 operations, zero-copy, bytes pools, scheduling, bandwidth, memory, disk I/O, errors, timeouts, retries, and tracked in-flight memory.

### Important APIs, Types, And Functions
Public modules include adaptive TTL, autotuner, backpressure, cache config, capacity, collector, config, deadlock, internode, I/O metrics, lock metrics, performance, process lock metrics, S3 API metrics, sampler, system path, timeout metrics, bandwidth, global metrics, and metric names. Re-exports expose core types and helpers. Internal statics `EC_ENCODE_INFLIGHT_BYTES` and `GET_OBJECT_BUFFERED_BYTES` back `add/remove/current_ec_encode_inflight_bytes` and `track/current_get_object_buffered_bytes`. `MemoryGaugeGuard` decrements a tracked gauge on drop. Top-level recorders cover GetObject lifecycle, zero-copy read/write/fallback/saved bytes, bytes pool activity, S3 get/put/list/delete, I/O strategy/load/permit wait, cache size, bandwidth/data transfer, memory split/cgroup, CPU/disk, errors/timeouts/retries, I/O latency, and zero-copy extension metrics.

### Control Flow
Most public functions are direct `metrics` macro calls. Memory tracking functions update atomics and set gauges; decrement uses a CAS-based saturating subtraction. `track_get_object_buffered_bytes` returns `None` for zero bytes or a `MemoryGaugeGuard` that decrements on drop. `record_data_transfer` computes bandwidth only if duration is positive. `record_bandwidth` records both an `"all"` tier gauge and a tier-specific gauge.

### State And Persistence
Local persistent state consists of two process-wide atomics for current in-flight byte gauges. Everything else is emitted to the configured metrics recorder. Drop guards provide scoped state cleanup for GET buffering.

### Dependencies And Integration Points
Imports metrics macros globally. Integrates with all submodules via re-exports and with `rustfs-obs` for OTEL exporter setup, per crate docs. It is the main downstream API surface.

### Risks
The file contains overlapping metric helpers with submodules, which can fragment naming if callers mix equivalent functions. Many labels accept `String` from arbitrary `&str` values, so cardinality discipline is caller-owned. `MemoryGaugeGuard` is not cloneable, which is good for ownership, but manual construction is possible inside tests only because fields are private. Metrics emission does not validate values; negative sizes cast to f64 can be recorded in some S3 paths when passed as `i64`, though most functions guard size > 0 before histograms.

### Test Signals
Unit tests execute top-level recording helpers, EC in-flight saturation, GET buffered-byte drop guard behavior, memory/cgroup recording, disk/error/timeout/retry helpers, and zero-copy metric constants/functions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/lib.rs -->
