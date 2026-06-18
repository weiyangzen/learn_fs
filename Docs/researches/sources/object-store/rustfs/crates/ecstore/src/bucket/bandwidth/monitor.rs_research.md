# sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/monitor.rs

Purpose: process-local bandwidth throttle and measurement subsystem keyed by bucket plus replication ARN.

Important APIs and types: `BucketThrottle` wraps a `ratelimit::Ratelimiter` and exposes `burst` and bulk-ish `consume`. `BucketMeasurement` tracks bytes in the current window and an exponential moving average. `BandwidthDetails` and `BucketBandwidthReport` are serializable reporting models. `Monitor` owns throttle and measurement maps plus cluster node count.

Control flow: `Monitor::new` clamps node count to at least one and spawns a two-second moving-average updater when inside a Tokio runtime. `set_bandwidth_limit` divides cluster limit by node count, creates a per-node throttle, and stores it. `update_measurement` fast-paths under read lock and inserts under write lock on miss. Delete methods remove all bucket throttles or one ARN.

State and persistence: all state is in memory behind standard locks and atomics; no persisted configuration. Reports multiply per-node limits back by node count.

Dependencies and integration points: used by bucket target replication throttling through `get_global_bucket_monitor`; depends on `ratelimit`, serde, tracing, and `BucketOptions`.

Risks: custom token consumption manipulates limiter availability because the crate lacks bulk consume. Very small limits clamp to one byte/sec per node. Moving-average retention uses a single start time, so `LastMinute` style precision is not present here.

Test signals: extensive unit tests cover limit splitting, deletion, invalid limits, token deficits, concurrency, poison recovery, report filtering, and current bandwidth updates.
