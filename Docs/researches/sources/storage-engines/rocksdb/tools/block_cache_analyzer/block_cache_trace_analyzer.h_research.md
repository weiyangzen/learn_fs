<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.h -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.h

## Purpose

`block_cache_trace_analyzer.h` declares the data model and public API for the RocksDB block-cache trace analyzer. It defines per-key, per-block, per-block-type, per-SST, and per-column-family aggregation structures, feature/prediction vectors for correlation analysis, and the `BlockCacheTraceAnalyzer` class used by the C++ command entry point.

## Important APIs, Types, And Functions

`GetKeyInfo` tracks a user key's assigned ID plus access sequence numbers and timestamps. `AddAccess()` appends the sequence number and microsecond timestamp for each Get access referencing that key.

`BlockAccessInfo` is the central per-block aggregate. It stores block identity, table and offset metadata, access counts, size, first/last access time, key cardinality, referenced-key maps, caller maps, per-caller timelines, unique blocks since last access, reuse-distance counts, sequence timelines, and timestamp timelines. `AddAccess()` enforces consistent block size/key count when known, updates caller and timeline data, records table/offset metadata, and gathers data-block Get/MultiGet spatial-locality fields.

`BlockTypeAccessInfoAggregate`, `SSTFileAccessInfoAggregate`, and `ColumnFamilyAccessInfoAggregate` form the nested aggregate tree used by the implementation: column family -> SST fd -> block type -> block key -> block info.

`Features` and `Predictions` store vectors for correlation analysis, pairing past features like elapsed time since last access and number of past accesses with future reuse intervals/access counts.

`BlockCacheTraceAnalyzer` exposes `Analyze()`, print methods, CSV writer methods, and `TEST_cf_aggregates_map()`. Private helpers parse label strings, build labels, compute reuse distance, record a single access, update reuse/correlation feature vectors, write generic bucket stats, and traverse blocks.

`block_cache_trace_analyzer_tool(int argc, char** argv)` declares the CLI entry point implemented in the `.cc` file.

## Control Flow

The header's contract centers on one call to `Analyze()` followed by zero or more print/write calls. `Analyze()` populates internal aggregate maps and simulator state. The writer methods then traverse this populated state to produce individual analyses.

`BlockAccessInfo::AddAccess()` is called once per full-analysis trace record. It updates basic metadata first, then caller/timeline maps, then data-block key-level fields when the access is a Get or MultiGet on a data block.

The private `TraverseBlocks()` callback pattern is the core extension point for output writers: it lets each writer supply a callback receiving column-family, file, level, block type, block key, block ID, and immutable block aggregate.

## State And Persistence Behavior

The analyzer owns all aggregation state. `cf_aggregates_map_` owns block records; `block_info_map_` stores pointers into that map and therefore depends on the map lifetime. `get_key_info_map_` accumulates key reuse features for Get accesses. Sequence and timestamp counters are monotonic across trace processing.

The header also declares output path fields (`output_dir_`, `human_readable_trace_file_path_`) and a `BlockCacheHumanReadableTraceWriter`. Actual file persistence is performed by implementation writers.

## Dependencies And Integration Points

The header depends on RocksDB internal and public headers: `db/dbformat.h` for key parsing support, `rocksdb/env.h`, `rocksdb/trace_record.h`, `rocksdb/utilities/sim_cache.h`, `trace_replay/block_cache_tracer.h`, and `utilities/simulator_cache/cache_simulator.h`.

Types such as `TraceType`, `TableReaderCaller`, `BlockCacheTraceRecord`, `BlockCacheTraceHelper`, `MissRatioStats`, and `BlockCacheTraceSimulator` are provided outside this header. This makes the analyzer tightly integrated with RocksDB's trace replay and simulator subsystems.

## Risks And Edge Cases

`BlockAccessInfo::AddAccess()` uses assertions for block-size/key-count consistency and referenced-data-size sanity. In release builds assertions may be disabled; in debug builds malformed traces can abort the process.

`CacheEntry`-like metadata in Python and C++ differ; this header's aggregation uses RocksDB-native fields and helper APIs, while the Python simulator consumes a positional CSV representation. Keeping those contracts synchronized is a cross-language maintenance risk.

`block_info_map_` contains raw pointers into nested `std::map` values. `std::map` node stability makes this workable for inserts, but future container changes would risk pointer invalidation.

Reuse-distance support stores `unique_blocks_since_last_access` per block, which can be very memory-intensive. The header's state shape makes that cost apparent even before reading the implementation.

## Test Signals

`TEST_cf_aggregates_map()` exposes the aggregation tree for tests. Key testable contracts include `BlockAccessInfo::AddAccess()` timeline updates, data-block key maps, column-family/SST/block-type nesting, and analyzer behavior with `mrc_only_` disabled vs enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.h -->
