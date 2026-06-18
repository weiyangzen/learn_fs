<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_test/src/lib.rs -->
# sources/storage-engines/tikv/components/engine_test/src/lib.rs

## Purpose
`engine_test/src/lib.rs` provides concrete engine type aliases and constructors for TiKV tests while keeping most test code generic over `engine_traits`. It centralizes how KV engines, raft engines, and tablet engines are created under feature-selected backends.

## Important APIs, Types, and Functions
The `raft` module exposes `RaftTestEngine` and `new_engine`. The `kv` module exposes `KvTestEngine`, iterator/snapshot/write-batch aliases, `new_engine`, `new_engine_opt`, and `TestTabletFactory`.

The `ctor` module defines `KvEngineConstructorExt` and `RaftEngineConstructorExt`, plus portable `DbOptions` and `CfOptions` structs. `DbOptions` carries key manager, rate limiter, state storage, and multi-batch-write flag. `CfOptions` carries selected RocksDB-style test options such as auto-compaction, L0 triggers, and disabling range/table properties.

Backend implementations include a panic-engine constructor, RocksDB constructors, and raft-log-engine raft constructor. RocksDB helpers translate generic options into `RocksDbOptions`/`RocksCfOptions`, install range and MVCC properties collectors unless disabled, configure encryption/rate-limited envs, enable multi-batch write when requested, and create range-filtered tablets with optional persistence listeners.

## Control Flow
Feature flags select public type aliases through `cfg`. KV/raft public constructors call the selected engine's constructor trait implementation. RocksDB `new_kv_engine` creates default CF options and delegates to `engine_rocks::util::new_engine_opt`. `new_kv_engine_opt` converts each generic CF option. `new_tablet` configures DB write mode for tablets, optionally installs a persistence listener from tablet context, attaches `RangeCompactionFilterFactory` to every CF, and opens the engine.

`TestTabletFactory` implements `TabletFactory` by opening tablets through the selected KV engine, destroying tablets through `encryption::trash_dir_all`, and checking existence through engine-specific `exists`.

## State and Persistence Behavior
Constructors create and destroy test storage directories. RocksDB tablet constructors install range compaction filters, so compaction can persistently remove keys outside the tablet range. `DbOptions` state is cloned into constructors but otherwise transient. `new_temp_engine` creates paired KV/raft engines under a temporary directory.

## Dependencies and Integration Points
This crate is the main test-suite integration point for `engine_rocks`, `engine_panic`, `raft_log_engine`, `engine_traits`, encryption, rate limiting, tablet state storage, and range/MVCC property collectors. It intentionally knows about concrete backends so other tests can avoid doing so.

## Risks and Edge Cases
The documentation notes constructor logic duplicates behavior from `engine_rocks::util`. Divergence can cause tests to run with different collector or option sets than production-like constructors. `path.to_str().unwrap()` assumes UTF-8 paths. Tablet setup assumes no existing compaction filter factory from `get_rocks_cf_opts`. Feature combinations must avoid ambiguous type aliases.

## Test Signals
The crate has no direct tests in this file, but all engine-trait integration tests depend on it. Important validation lanes are default features, all-RocksDB tests, panic-engine tests, tablet lifecycle tests, encrypted env tests, rate-limiter propagation, multi-batch-write construction, and no-range/no-table-properties options.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_test/src/lib.rs -->
