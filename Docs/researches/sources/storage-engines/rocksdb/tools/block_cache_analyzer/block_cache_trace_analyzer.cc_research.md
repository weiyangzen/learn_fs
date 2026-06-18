<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.cc -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.cc

## Purpose

`block_cache_trace_analyzer.cc` implements the RocksDB block-cache trace analyzer command when built with `GFLAGS`. It reads binary or human-readable block-cache traces, optionally simulates cache configurations, aggregates per-block/per-file/per-column-family statistics, and emits human-readable summaries plus CSV files for timelines, miss-ratio curves, reuse metrics, spatial locality, skew, access-count distributions, and correlation inputs.

## Important APIs, Types, And Functions

The file defines gflags for trace path, output path, cache simulator config, downsample/warmup, print options, grouping labels, bucket lists, reuse analysis, caller analysis, MRC-only mode, correlation limits, and human-readable trace conversion.

Helper functions convert block types and callers to strings, parse caller names, identify user accesses, compute percentages, parse bucket strings, parse cache simulator configuration files, and normalize timeline granularity.

`BlockCacheTraceAnalyzer::Analyze()` is the main reader loop. It creates either `BlockCacheHumanReadableTraceReader` or binary `BlockCacheTraceReader`, optionally opens a human-readable writer, streams records, records per-block state unless `mrc_only_`, updates miss-ratio stats, feeds `BlockCacheTraceSimulator`, and prints progress.

`RecordAccess()` updates the nested aggregate maps keyed by column family, SST file number, block type, and block key. It assigns stable internal block IDs, updates `BlockAccessInfo`, tracks Get key timelines, optionally computes reuse distance, and writes a human-readable record with block/get IDs.

Output writers include `WriteMissRatioCurves()`, `WriteMissRatioTimeline()`, `WriteMissTimeline()`, `WriteAccessTimeline()`, `WriteReuseDistance()`, `WriteReuseInterval()`, `WriteReuseLifetime()`, `WriteBlockReuseTimeline()`, `WritePercentAccessSummaryStats()`, `WriteDetailedPercentAccessSummaryStats()`, `WriteAccessCountSummaryStats()`, `WriteGetSpatialLocality()`, `WriteSkewness()`, `WriteCorrelationFeatures()`, and `WriteCorrelationFeaturesForGet()`.

Print-only methods include `PrintStatsSummary()`, `PrintBlockSizeStats()`, `PrintAccessCountStats()`, and `PrintDataBlockAccessStats()`.

`block_cache_trace_analyzer_tool()` is the command entry point. It parses flags, initializes optional cache simulators, constructs the analyzer, runs analysis, writes MRC/timelines, and dispatches all requested detailed analyses unless MRC-only mode is set.

## Control Flow

Startup validates `FLAGS_block_cache_trace_path`, parses cache simulator configs if provided, and constructs `BlockCacheTraceSimulator` with warmup and downsample settings. The analyzer then reads the trace until the reader returns an incomplete/end status or an error.

During each record, full-analysis mode calls `RecordAccess()` before updating global miss-ratio state. The simulator access path is independent of full-analysis state, which lets `--mrc_only` avoid keeping per-block aggregates while still producing cache simulation outputs.

After analysis, the entry point always writes miss-ratio curves and miss/miss-ratio timelines for 1 second, 1 minute, and 1 hour granularities if a simulator/output directory exists. It then prints summaries and conditionally writes optional outputs based on non-empty label/bucket flags.

Most CSV writers use `TraverseBlocks()` to iterate the nested aggregate tree and build label-keyed maps. `ParseLabelStr()` validates labels such as `cf`, `sst`, `level`, `bt`, `caller`, `block`, and `all`; `BuildLabel()` concatenates selected label values into stable output labels.

## State And Persistence Behavior

Persistent analyzer state lives in memory while processing a trace: `cf_aggregates_map_` owns block aggregate data, `block_info_map_` points into those owned block aggregates for quick lookup, `get_key_info_map_` stores Get-key timelines, `miss_ratio_stats_` and `caller_miss_ratio_stats_map_` store time-bucketed hit/miss data, and `cache_simulator_` stores simulated cache state.

Reuse distance mode is particularly expensive. On every access, `RecordAccess()` can add the current block key to every existing block's `unique_blocks_since_last_access` set, making CPU and memory scale poorly with unique block count.

Output files are written directly under `output_dir_` with names encoding labels, time units, cache capacity, and suffix constants. Human-readable trace conversion writes to `human_readable_trace_file_path_` when requested. Most writers silently return if an output file cannot be opened.

## Dependencies And Integration Points

The file is compiled only under `#ifdef GFLAGS`. It depends on RocksDB trace classes (`BlockCacheTraceReader`, `BlockCacheHumanReadableTraceReader`, `BlockCacheTraceRecord`), RocksDB cache simulator classes, `Env`/file APIs, `HistogramStat`, gflags compatibility, and RocksDB string parsing utilities.

`parse_cache_config_file()` consumes configuration lines matching `cache_name,num_shard_bits,ghost_capacity,cache_capacity_1,...`. These map into `BlockCacheTraceSimulator` and the output contract used by plotting.

CSV outputs use suffixes and layouts expected by `block_cache_trace_analyzer_plot.py`. The Python simulator produces parallel `ml_*` variants for some of the same graph families.

## Risks And Edge Cases

Many output writers silently return when a file cannot be opened, so a run can finish without producing requested files. Several bucketed analyses use `upper_bound(...)->second` and require the final max bucket appended by `parse_buckets()`; direct calls with incomplete buckets can dereference `end()`.

`TraverseBlocks()` returns immediately when grouping by table and a block lacks table ID, which can stop traversal of all remaining blocks rather than skipping only that block. This can under-report table-grouped analyses.

`Analyze()` returns the final reader status. The tool treats `Status::Incomplete()` as successful end-of-trace, but any other non-OK status exits. Consumers need to know that incomplete is normal here.

Reuse distance computation is explicitly high-cost and can become impractical for large traces. Timeline writers can also create wide CSVs from `start_time` to `end_time`, with sparse data expanded into zero-filled columns.

Some percentage calculations return `-1` on zero denominators; those values are written into CSVs and can surprise plotting or downstream consumers expecting non-negative percentages.

## Test Signals

This file exposes `TEST_cf_aggregates_map()` in the header, suggesting unit tests can inspect aggregation state. The code itself contains no tests in this subset. Practical validation signals are compile coverage under `GFLAGS`, analyzer invocation on representative traces, output-file existence/content checks, and plotting compatibility checks against generated CSVs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.cc -->
