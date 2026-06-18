# sources/storage-engines/rocksdb/db/internal_stats.cc

## Purpose

`internal_stats.cc` implements RocksDB's internal property and statistics plumbing for column families and DB instances. It turns live `ColumnFamilyData`, `VersionStorageInfo`, `DBImpl`, cache, blob, memtable, write-stall, and compaction state into user-visible `DB::Properties` strings, integer values, and map properties. It also owns the formatter logic for compaction level tables, DB/CF cumulative and interval stats, file read latency histograms, block-cache entry role accounting, blob stats, and integer property aggregation across column families.

This file is not a persistence layer itself. Its state is in-memory telemetry attached to `InternalStats`; the persisted data it reports comes from `Version`, MANIFEST-derived `VersionStorageInfo`, table properties, WAL counters, and DB runtime controllers.

## Important APIs, types, and functions

- `InternalStats::compaction_level_stats` and `db_stats_type_to_info` define the property-name vocabulary for level compaction metrics and DB counters.
- `DB::Properties::k...` string constants are defined here from the `rocksdb.` prefix plus property suffixes. They are the public property keys consumed by `DB::GetProperty`, `GetIntProperty`, and `GetMapProperty`.
- `InternalStats::ppt_name_to_info` is the central dispatch table from property name to `DBPropertyInfo`, selecting one of string, integer, map, or `DBImpl` string handlers and marking whether the property must be collected outside the DB mutex.
- `GetPropertyInfo()` strips a trailing numeric suffix and resolves the property in the dispatch table.
- `InternalStats::GetStringProperty()`, `GetMapProperty()`, `GetIntProperty()`, and `GetIntPropertyOutOfMutex()` route property requests to the registered handler.
- Formatting helpers `PrepareLevelStats()`, `PrintLevelStatsHeader()`, and `PrintLevelStats()` compute and render level, priority, and summary compaction rows.
- `DumpCFMapStats()`, `DumpCFStatsNoFileHistogram()`, `DumpCFFileHistogram()`, `DumpDBMapStats()`, and `DumpDBStats()` are the core emission paths.
- `CacheEntryRoleStats::{BeginCollection,GetEntryCallback,EndCollection,SkippedCollection,ToString,ToMap}` provide block-cache entry role collection output for `CacheEntryStatsCollector`.
- Blob handlers expose blob-file counts, total/live/garbage size, blob stats text, and blob-cache capacity/usage/pinned usage.
- `CreateIntPropertyAggregator()` returns either a normal summing aggregator or a block-cache aggregator that de-duplicates shared cache instances across column families.

## Control flow

Property lookup starts with `GetPropertyInfo()`, which uses `GetPropertyNameAndArg()` to separate a trailing decimal argument from the property key. The caller then invokes the correct `InternalStats::Get*Property` method. String and map properties receive the suffix directly; integer properties either require `DBImpl::mutex_` or, for the small set marked `need_out_of_mutex`, receive a stable `Version*`.

For CF stats, handlers call `DumpCFMapStats()` or `DumpCFStats()`. The map path computes per-level metrics from current `VersionStorageInfo`, current compaction stats, L0/flush ingest counters, file sizes, compaction scores, files being compacted, and write-stall counters. The string path renders the same data, adds interval stats by subtracting `cf_stats_snapshot_`, emits priority-grouped compaction rows, blob summary, uptime, ingest and compaction bandwidth, pending compaction bytes, write-stall text, and the latest cached block-cache entry role stats when recent enough. File-read histograms are appended separately.

For DB stats, `DumpDBStats()` reads atomic DB counters, computes cumulative and interval write/WAL/stall rates, formats write-stall count breakdowns, and then updates `db_stats_snapshot_` so the next call reports a new interval. `DumpDBMapStats()` emits current raw counters plus uptime without updating interval snapshots.

The periodic CF handler uses `has_cf_change_since_dump_`, `last_histogram_num`, `no_cf_change_period_since_dump_`, and `kMaxNoChangePeriodSinceDump` to avoid emitting unchanged stats every period while still forcing an occasional dump.

## State and persistence behavior

Most counters are in-memory: `db_stats_` atomics, `cf_stats_value_`, `cf_stats_count_`, `comp_stats_`, `comp_stats_by_pri_`, `per_key_placement_comp_stats_`, read latency histograms, background error count, and running sorted-run count. `started_at_` anchors uptime. `db_stats_snapshot_` and `cf_stats_snapshot_` are mutable interval baselines; calls to `DumpDBStats()` and periodic CF dumps can change future output.

The file reads persisted metadata indirectly through `cfd_->current()`, `VersionStorageInfo`, table properties collection, blob file metadata, and `DBImpl` file-number/log state. It does not write on-disk state. The block-cache stats collector is held by `shared_ptr` and may be pinned in cache so subsequent stats calls can reuse previous scans.

## Dependencies and integration points

The implementation depends on `DBImpl`, `ColumnFamilyData`, `Version`, `VersionStorageInfo`, `MemTableList`, compaction picker state, write controller state, `WriteStallStatsMapKeys`, table properties APIs, block-based table cache options, blob metadata, `CacheEntryStatsCollector`, `HistogramImpl`, and formatting helpers from `util/string_util.h`.

It integrates with the public RocksDB property APIs through `DB::Properties` constants and `DBPropertyInfo`; with write/flush/compaction code through `InternalStats::Add*` methods declared in the header; with cache code through `CacheEntryStatsCollector`; with multi-CF property aggregation through `IntPropertyAggregator`; and with DB mutex discipline through `need_out_of_mutex` and the assertion in `GetIntProperty()`.

## Risks and edge cases

- `GetPropertyNameAndArg()` treats any trailing digits as a suffix and assumes property base names do not end in digits. Adding a digit-ending property name would break lookup unless the convention is preserved.
- Some stats reads mutate interval snapshots. Repeated calls to textual DB stats or periodic CF stats are observably stateful.
- `AddDBStats(..., concurrent=false)` performs load-plus-store with relaxed atomics and is only safe where callers already serialize updates.
- Several handlers dereference `cfd_->current()` and related metadata under assumptions supplied by higher-level locking or version lifetime management.
- `HandleEstimateTableReadersMem()` returns `0` if no `Version*` is supplied, so using it through the wrong path would silently under-report.
- Cache entry stats can be stale by design. Fast/background paths intentionally stretch collection intervals to limit scan overhead.
- The map/string stats logic uses many manual divisions and counters; zero denominators are mostly guarded with `max()` or explicit checks, but changes to interval logic can reintroduce divide-by-zero or misleading rates.

## Test signals

The nearest direct coverage is usually in DB property, options/statistics, blob, write-stall, and cache tests rather than this file alone. Useful signals include tests that verify `DB::Properties` keys, map property names, block-cache capacity aggregation across column families, blob file stats, write-stall counters, compaction reason counts, table properties aggregation, and periodic stats output. `listener_test.cc` in this work item indirectly validates some data surfaced here, such as compaction job stats, blob file metadata, and table properties in event callbacks.
