# sources/storage-engines/tikv/src/server/engine_factory.rs

## Purpose

This file builds TiKV KV RocksDB engines for both shared RaftKV and per-region tablet RaftKV2 layouts. It centralizes RocksDB option construction, column-family option construction, event listener wiring, tablet creation, tablet destruction, and the state-persistence listener used when WAL is disabled in v2. It is the bridge between `TikvConfig`/RocksDB resources and `engine_traits::TabletFactory<RocksEngine>`.

## Important APIs, Types, And Functions

- `FactoryInner` stores shared immutable construction inputs: `RegionInfoAccessor`, `DbConfig`, API version, flow listener, SST recovery scheduler, encryption key manager, shared DB/CF resources, optional `StateStorage`, and `lite` mode.
- `KvEngineFactoryBuilder::new` derives RocksDB and CF resources from `TikvConfig`, cache, Rocks env, and force-partition range manager.
- Builder setters install region metadata, flow listener, SST recovery scheduler, compaction-event sender, lite mode, and v2 state storage.
- `KvEngineFactory::create_raftstore_compaction_listener` creates a `CompactionListener` only when a compacted-event sender exists, and filters compaction events to write/default CF output levels >= 2 for region-size accounting.
- `db_opts` builds `RocksDbOptions` and, outside lite mode, adds the generic Rocks event listener plus the raftstore compaction listener.
- `cf_opts` delegates to `DbConfig::build_cf_opts`, optionally with a `RangeCompactionFilterFactory` for tablets.
- `create_shared_db` opens `path/DEFAULT_ROCKSDB_SUB_DIR` as a RaftKv engine.
- `TabletFactory<RocksEngine>` implementation opens/destroys tablets and checks existence.

## Control Flow

Shared DB creation builds RaftKv DB options and CF options without a range compaction filter, attaches the flow listener if configured, then opens RocksDB under the configured RocksDB subdirectory. Tablet creation builds RaftKv2 DB options, changes the info log to a tablet-specific `TabletLogger`, creates a `RangeCompactionFilterFactory` from the tablet context start/end keys, attaches tablet-specific flow and persistence listeners, and opens the database at the tablet path. On success it notifies the flow listener with `on_created`; destruction logs the tablet identity, trashes the tablet directory with encryption-aware deletion, and notifies `on_destroyed`.

## State And Persistence Behavior

Most factory state is held behind `Arc<FactoryInner>` and cloned into factory instances. Shared RocksDB resources and CF resources are constructed once in the builder and reused by later opens. When `state_storage` and `ctx.flush_state` are present, `open_tablet` installs `RocksPersistenceListener`, which persists flush state for WAL-disabled v2 recovery. Tablet destruction currently removes the directory via `encryption_export::trash_dir_all`; the commented RocksDB destroy path notes a future replacement.

## Dependencies And Integration Points

The file integrates `engine_rocks` option/listener APIs, `engine_traits` tablet factory abstractions, `raftstore::RegionInfoAccessor`, `ForcePartitionRangeManager`, encrypted directory deletion, TiKV config resource builders, and `tikv_util::worker::Scheduler` for SST recovery. It depends on TiKV API version selection because CF options may differ between API modes.

## Risks

- `path.to_str().unwrap()` and `file_name().unwrap()` assume valid UTF-8 paths and valid tablet path shape.
- `destroy_tablet` ignores the result of `trash_dir_all`, so deletion failures can be hidden from callers.
- `set_state_storage` under `testexport` mutates through a raw pointer to shared `Arc` data and must remain test-only.
- Lite mode suppresses listeners/filters, so users must not expect compaction events, flow metrics, or SST recovery behavior in that mode.
- The range compaction filter on tablets is correctness-sensitive because it removes keys outside tablet range.

## Test Signals

`test_engine_factory` verifies tablet existence, duplicate open locking, destruction, and post-destroy absence. `test_engine_factory_compaction_filter` verifies the tablet range compaction filter removes keys outside `[start_key, end_key)` while retaining in-range keys after flush.
