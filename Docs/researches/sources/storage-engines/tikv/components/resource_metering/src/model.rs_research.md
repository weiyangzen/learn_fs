# sources/storage-engines/tikv/components/resource_metering/src/model.rs

## Purpose
`model.rs` defines the core data model and aggregation algorithms for resource metering. It represents raw sampled usage, groups records by resource tag or region, selects top resource consumers, rolls the rest into "others", and converts internal structures into `kvproto` usage records.

## Important APIs, Types, And Functions
`RawRecord` stores CPU time, per-pool CPU time, read/write keys, logical IO, and network bytes. `add_cpu_time`, `merge`, and `merge_summary` update it. `RawRecords` is a time-windowed map from `Arc<TagInfos>` to `RawRecord` and can aggregate by extra tag or by extra tag plus region.

`find_kth_cpu_time`, `find_kth_values`, `get_iter_for_cpu_time`, and `get_iter_for_cpu_network_io` implement top-N selection using thread-local reusable buffers and `pdqselect`. `handle_records_impl` appends selected records and merges unselected records to "others", optionally considering network/logical IO as well as CPU.

`Record` stores per-timestamp vectors and validates aligned lengths before conversion. `Records` stores tag-keyed records plus timestamp-keyed others and converts into `ResourceUsageRecord` with `GroupTagRecord`. `RegionRecords` mirrors this for region IDs and `RegionRecord`. `SummaryRecord` provides atomic counters for request summaries, with clone, reset, merge, and take-and-reset operations. `RegionCpuRecord` accumulates total and per-pool CPU into region-level records.

## Control Flow
Recorder produces `RawRecords` for a sampling window. Reporter aggregates by tag and region, selects top groups up to configured limits, appends selected values by timestamp, merges unselected values into `others`, and finally converts accumulated records into protobuf messages for upload. Summary counters from thread-local request guards can be merged into raw records before final aggregation.

## State And Persistence Behavior
Aggregation state is in memory. `Records` and `RegionRecords` retain per-tag/per-region vectors until cleared. `SummaryRecord` fields are atomics so request paths can update counters cheaply and safely. Thread-local buffers reduce repeated allocation during top-K selection but require correct clear/set discipline.

## Dependencies And Integration Points
The model depends on `collections::HashMap`, `kvproto::resource_usage_agent` messages, `pdqselect`, `Arc<TagInfos>`, and `tikv_util::warn`. It is used by recorder, collector, and reporter modules and by public re-exports from `lib.rs`.

## Risks
Top-N selection uses strict `>` comparisons against kth values, so ties at the threshold are rolled into "others"; this is intentional and covered by an issue regression test but can return fewer than N explicit records. Conversion skips invalid `Record` vector shapes after logging. Accumulators use integer addition without saturation in several paths, so extreme long-running accumulations could overflow if not periodically cleared. Thread-local reusable buffers make selection efficient but not reentrant within a thread.

## Test Signals
Tests cover `SummaryRecord` operations, tag aggregation, top-K CPU selection, tie handling for issue 12234, aggregation by repeated extra tags, aggregation by region, and top-K selection across CPU/network/logical IO.
