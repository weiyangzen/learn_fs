<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/examples/metrics_example.rs -->
## sources/object-store/rustfs/crates/io-metrics/examples/metrics_example.rs

### Purpose
Runnable example demonstrating cache configuration, adaptive TTL, access tracking, unified I/O configuration, and basic metric recording through the `rustfs_io_metrics` public API.

### Important APIs, Types, And Functions
Uses `CacheConfig`, `AdaptiveTTL`, `AccessTracker`, `IoConfig`, `CacheSettings`, `IoSchedulerSettings`, and `record_cache_size`. The example functions are `cache_config_example`, `adaptive_ttl_example`, `access_tracker_example`, `unified_config_example`, and `metrics_recording_example`.

### Control Flow
`main` prints a heading and calls the five example sections. The cache example builds default and custom configs and validates them. The TTL example calculates TTLs for several access counts and checks early eviction. The access tracker simulates hot/warm/cold object accesses and prints counts and classifications. The unified config example composes cache and scheduler settings. The metrics example loops ten times and emits cache-size gauges with hit/miss commentary.

### State And Persistence
All state is local to the example process: in-memory tracker records, config structs, and metrics macro emissions. There is no persistent output beyond stdout and any metrics recorder side effects.

### Dependencies And Integration Points
Documents intended crate usage for downstream RustFS components and human developers. It relies on public re-exports from `lib.rs`.

### Risks
The metrics recording example uses `record_cache_size` as a stand-in for hit/miss activity, which does not actually record cache hits or misses. This can mislead readers unless treated as a simple macro-emission demonstration rather than semantic cache accounting.

### Test Signals
Not a test, but `cargo run --example metrics_example` can validate public API compileability and produce sample output.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/examples/metrics_example.rs -->
