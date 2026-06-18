<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/util.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/util.rs

## Purpose
`util.rs` provides RocksDB engine construction helpers, RocksDB property helpers, slice transforms, perf-level conversion, and compaction filter composition/range filtering. It is shared by tests, engine constructors, metrics, and tablet creation code.

## Important APIs, Types, and Functions
Engine constructors include `new_temp_engine`, `new_default_engine`, `new_engine`, and `new_engine_opt`. `new_engine_opt` handles create/open, CF reconciliation, dynamic-level-byte preservation, missing CF creation, and dropping unneeded CFs.

Storage helpers include `db_exist`, `get_cf_handle`, `range_to_rocks_range`, `get_engine_cf_used_size`, `get_engine_cfs_used_size`, `get_engine_compression_ratio_at_level`, level/blob file-count getters, immutable memtable count, and pending compaction bytes.

`FixedSuffixSliceTransform`, `FixedPrefixSliceTransform`, and `NoopSliceTransform` implement RocksDB `SliceTransform`. `to_raw_perf_level` and `from_raw_perf_level` bridge perf-level enums.

`StackingCompactionFilterFactory` and `StackingCompactionFilter` compose two RocksDB compaction filter factories/filters in outer-then-inner order. `RangeCompactionFilterFactory` and `RangeCompactionFilter` remove keys outside a configured range, using `RemoveAndSkipUntil`.

## Control Flow
`new_engine_opt` rejects configurations without default CF. If no DB exists it enables DB/CF creation and opens directly. For existing DBs, it lists existing CFs, loads latest options when CFs exist, adds default options for unknown existing CFs so the DB can open, preserves old dynamic-level-byte settings per CF, opens with missing CF creation if needed, then drops CFs not requested.

Property helpers query RocksDB integer/string properties and handle Titan optional properties when present. Range filters decide outside-low, outside-high, or keep. Stacked filters precompute which creation reasons each factory wants, then create only needed filters for the current table-file creation reason.

## State and Persistence Behavior
Engine construction creates DB directories, creates missing CFs, and drops unneeded CFs from existing DBs. `RangeCompactionFilter` affects persisted SST contents by removing out-of-range keys during compaction. Property helpers are read-only. Slice transforms affect RocksDB prefix extraction and therefore read/write behavior for configured CFs.

## Dependencies and Integration Points
It depends on `RocksDbOptions`, `RocksCfOptions`, `RocksStatistics`, RocksDB options/open/property APIs, `engine_traits` ranges/engines, `rocks_metrics_defs`, `keys`, failpoints, and `slog_global::warn`. `engine_test` uses these constructors for RocksDB-backed test engines and tablet factories.

## Risks and Edge Cases
`db_exist` unwraps `read_dir`, so unreadable directories can panic. Preserving dynamic-level-byte settings avoids corruption but silently overrides requested changes after warning. Opening existing DBs depends on `OPTIONS` files; missing options trigger panic. Dropping CFs is destructive for data in unrequested CFs. Slice transforms assume keys are at least prefix/suffix length after `in_domain`; direct `transform` calls on short keys would panic.

`RangeCompactionFilter` asserts keys above the configured end are below `DATA_MAX_KEY` and skips to `DATA_MAX_KEY`, so it is specific to TiKV data-key ranges. The `unlimited_range_compaction_filter` failpoint broadens filtering to all data keys.

## Test Signals
Tests cover CF diffing, create/add/reorder/drop CF flows, dynamic-level-byte preservation, default CF requirement, and range compaction filtering for puts/deletes around range bounds. Additional tests should cover missing OPTIONS, unreadable directories, stacked filter ordering, and property helper behavior under missing Titan properties.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/util.rs -->
