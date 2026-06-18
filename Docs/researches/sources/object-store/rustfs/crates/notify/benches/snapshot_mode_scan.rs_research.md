# sources/object-store/rustfs/crates/notify/benches/snapshot_mode_scan.rs

Purpose: Criterion benchmark comparing `starshard::AsyncShardedHashMap` snapshot modes when scanning notification rule maps for a target ID.

Important APIs/types/functions: `build_rule_map` creates a `RulesMap` with an ObjectCreatedPut wildcard rule for one `TargetID`. `build_map` creates an async sharded map with selected `SnapshotMode` and fills `bucket-{i}` entries. `scan_target_bound` iterates a snapshot and returns true if any rules map contains the target. `bench_snapshot_mode_scan` runs Clone vs Cached modes for 1,000 and 10,000 buckets.

Control flow: a Tokio runtime is created inside the benchmark. For each size/mode pair, setup builds the map once, then Criterion repeatedly scans for a missing target to force a full traversal. Throughput is recorded as bucket elements.

State and persistence: in-memory benchmark data only; no external state. The map uses `FxBuildHasher`, `DEFAULT_SHARDS`, and the selected snapshot caching strategy.

Dependencies/integration: imports `rustfs_notify::rules::RulesMap`, `rustfs_targets::arn::TargetID`, `rustfs_s3_types::EventName`, `starshard`, Tokio runtime, and Criterion. It benchmarks a core rule-engine access pattern: target-bound full-map scans.

Risks: uses a missing target only, so it measures worst-case scan but not early-hit behavior. Runtime creation and `block_on` inside iterations add async overhead. Benchmark does not vary rule complexity per bucket.

Test signals: not a unit test; run with `cargo bench -p rustfs-notify --bench snapshot_mode_scan`. It provides performance regression signals for snapshot mode changes.
