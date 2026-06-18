# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/size.rs

## Purpose
`size.rs` implements size-based split checking and approximate region-size helpers. It updates raftstore with approximate sizes, decides whether size or bucket checks are needed, and produces split keys by scan byte accounting or engine range properties.

## Important APIs, Types, And Functions
`Checker` tracks `max_size`, `split_size`, `current_size`, `split_keys`, `batch_split_limit`, and `policy`. `SizeCheckObserver<C>` owns a `StoreHandle`. `get_region_approximate_size` wraps `KvEngine::get_range_approximate_size`; `get_approximate_split_keys` wraps `KvEngine::get_range_approximate_split_keys` over encoded region bounds.

## Control Flow
`SizeCheckObserver::add_checker` reads approximate region size up to `region_max_size * batch_split_limit`. On failure it logs and adds a scan checker. On success it sends `UpdateApproximateSize`, observes the histogram, and adds a checker if the region exceeds max size or if region buckets are enabled and the region is at least two bucket sizes. Large regions switch policy to `Approximate` once above `region_size_threshold_for_approximate`; bucket-only checks can also prefer approximate.

During scans, `Checker::on_kv` adds `entry_size`, emits a split key when `current_size > split_size`, and preserves the current entry size when the previous total was exactly the split size. It can stop once batch limit is reached and enough size was scanned for the last part. `split_keys` removes the final key if the trailing part would be smaller than `max_size`. Approximate split mode computes split-key count via `calc_split_keys_count` and asks the engine for approximate keys.

## State And Persistence Behavior
State is per checker run. Persistent effects are indirect: approximate size updates and eventual split/bucket tasks sent through `StoreHandle`. The helper functions read engine properties but do not mutate engine state.

## Dependencies And Integration Points
Uses engine range properties across large column families, `StoreHandle`, split-check host/config, metrics, and raftstore split-check runner expectations. Size checking is registered by default before keys checking, which matters for scan reuse and policy escalation.

## Risks
Approximate range properties can be inaccurate for small, unflushed, compacting, or property-disabled data. Boundary handling around `current_size`, `split_size`, and final key popping is subtle and has regression tests. If approximate helpers error due to missing range properties, scan fallback protects split checking but may increase IO. `merge` of split results with bucket generation is order-sensitive because host returns the first non-empty checker result.

## Test Signals
Tests cover scan splits across CFs, approximate bucket generation for normal and MVCC keys, bucket policy selection, CF_LOCK without range properties, edge cases where max equals or doubles split size, approximate split-key errors and outputs, approximate size calculations, inaccurate subrange-size behavior, and a benchmark for approximate size.
