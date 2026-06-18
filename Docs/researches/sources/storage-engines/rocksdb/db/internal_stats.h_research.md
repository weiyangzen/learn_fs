# sources/storage-engines/rocksdb/db/internal_stats.h

## Purpose

`internal_stats.h` declares the `InternalStats` class, related property dispatch metadata, compaction and cache statistics containers, and integer property aggregation interface used by RocksDB DB/column-family property reporting. It is the shared contract between code that records runtime counters and code that exposes those counters through `DB::Properties`.

The header centralizes in-memory DB/CF telemetry shape: write-stall counters, compaction byte and record counters, flush and external file ingestion counters, read latency histograms, blob read/write stats, cache entry role summaries, interval snapshots, and background error counts.

## Important APIs, types, and functions

- `DBPropertyInfo` stores the dispatch metadata for one property: mutex requirements and exactly one handler pointer for string, integer, map, or `DBImpl`-owned string properties.
- `GetPropertyInfo(const Slice&)` returns the dispatch metadata for a public property key.
- `LevelStatType`, `LevelStat`, and `DBStatInfo` define typed stat identifiers and public map/header names.
- `InternalStats::InternalCFStatsType` enumerates CF counters for write stalls, flush bytes, external file ingestion, file counts, and key counts.
- `InternalStats::InternalDBStatsType` enumerates DB counters for WAL bytes/syncs, write bytes/keys/groups, writes with WAL, write stall micros, and write-buffer-manager stops.
- `CompactionStats` stores per-output-level compaction counters and per-`CompactionReason` counts. It implements copy/assignment, `Clear()`, `Add()`, `Subtract()`, and `ResetCompactionReason()`.
- `CompactionStatsFull` wraps primary and optional proximal-level output stats for per-key-placement compaction and exposes `TotalBytesWritten()`, `DroppedRecords()`, `SetMicros()`, and `AddCpuMicros()`.
- `CacheEntryRoleStats` is the value type collected by `CacheEntryStatsCollector`; it can emit text and map forms.
- Public mutators such as `AddCompactionStats()`, `IncBytesMoved()`, `AddCFStats()`, `AddDBStats()`, and running sorted-run increment/decrement methods are the recording API.
- Property handlers are private methods named `Handle...` and are bound from the `.cc` property table.
- `IntPropertyAggregator` and `CreateIntPropertyAggregator()` define aggregation behavior across column families.

## Control flow

DB and compaction subsystems update `InternalStats` as work completes or runtime conditions change. Compactions add `CompactionStats` to a level and priority bucket. Flush and ingestion paths increment CF stat values and counts. DB writes increment atomic DB counters. Read paths update histograms through `GetFileReadHist()` and `GetBlobFileReadHist()`. Background errors are counted through `BumpAndGetBackgroundErrorCount()`.

Property reads enter through dispatch helpers declared here. String and map properties are served by private formatting handlers; integer properties may be served either while holding the DB mutex or outside the mutex with a supplied `Version*`, depending on `DBPropertyInfo::need_out_of_mutex`.

`Clear()` resets DB and CF counters, compaction stats, histograms, interval snapshots, background error count, uptime baseline, and periodic dump dirty state. It intentionally leaves the running compaction sorted-run atomic out of the generic reset path because that metric can both increment and decrement and should not be zeroed at periodic intervals.

## State and persistence behavior

`InternalStats` stores volatile telemetry only. Counters and snapshots live in memory and reset with `Clear()` or DB/CF object lifetime. Persistent file, table, blob, and version metadata are held elsewhere and only referenced through `ColumnFamilyData`, `Version`, and `VersionStorageInfo` in the implementation.

The class owns arrays of atomics for DB stats, raw arrays for CF counters, per-level and per-priority compaction vectors, read latency histograms, cache stats collector pointer, interval snapshots, and pointers to `SystemClock` and `ColumnFamilyData`. Because `cfd_` and `clock_` are raw pointers, lifetime is expected to be managed by the DB/column-family owner.

## Dependencies and integration points

The header depends on cache entry roles, `VersionSet`/`ColumnFamilyData`, `SystemClock`, RocksDB cache APIs, histograms, compaction reason enums, write-stall enums, table property types, and hash containers. It is included by DB implementation, compaction, flush, property, and test code that needs to update or inspect internal statistics.

The `TEST_` accessors expose CF stat arrays, compaction stats, per-key-placement compaction stats, and cache entry stats for unit tests. `IntPropertyAggregator` supports DBImpl-level aggregation of integer properties across all column families.

## Risks and edge cases

- Raw arrays are indexed by enum values; enum ordering and `*_ENUM_MAX` sentinels must remain consistent with array sizes.
- `CompactionStats::Subtract()` uses unsigned fields and assumes the subtracted snapshot is not newer/larger than the current stats. Incorrect ordering can underflow.
- `CompactionStatsFull::DroppedRecords()` only compares primary input records against combined outputs; users need to understand how proximal outputs affect drop accounting.
- `AddDBStats(concurrent=false)` is not an atomic read-modify-write despite using atomics. Callers must choose the concurrent mode correctly.
- `Clear()` resets interval baselines and most telemetry, making post-clear stats discontinuous.
- `CacheEntryRoleStats::ToMap()` computes used percent from cache capacity; callers should avoid zero-capacity cache configurations or be prepared for unusual floating output.

## Test signals

Relevant tests should exercise property lookup, counter increments, compaction stat accumulation/subtraction, reason counts, per-key-placement proximal stats, cache entry stats collection, write-stall stat mapping, and DB/CF stat clearing. Existing RocksDB DB property and listener tests provide indirect coverage by checking compaction payloads, table properties, blob stats, and write-stall pressure notifications.
