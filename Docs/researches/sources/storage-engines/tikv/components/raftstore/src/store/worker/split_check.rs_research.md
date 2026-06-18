# sources/storage-engines/tikv/components/raftstore/src/store/worker/split_check.rs

Purpose: this worker evaluates whether a region should split and refreshes region bucket metadata. It supports scan-based and approximate split policies, routes split requests back to the store, updates approximate size/key metadata, and processes compaction events that affect split heuristics.

Important APIs and types:
- `KeyEntry` wraps a key/value-size/CF tuple from merged CF iteration. Its ordering reverses key order so `BinaryHeap` works as a min-heap.
- `MergedIterator` merges iterators from `LARGE_CFS` over an encoded key range.
- `BucketRange`, `Bucket`, and `BucketStatsInfo` manage bucket boundaries, bucket sizes, bucket write-flow deltas, report deltas, and version retention.
- `Task<EK>` includes `SplitCheckTask`, `ApproximateBuckets`, `ChangeConfig`, `CompactedEvent`, and a test-only `Validate`.
- `Runner<EK, S>` owns either a direct engine or tablet registry, a store router implementing `StoreHandle`, a coprocessor host, and an optional region info provider.

Control flow:
- `Task::SplitCheckTask` calls `check_split_and_bucket`. The method resolves the active tablet, computes encoded scan bounds from the whole region or raw request range, builds a `SplitCheckerHost`, and exits if the host says to skip.
- For `CheckPolicy::Scan`, `scan_split_keys` iterates large CFs with `MergedIterator`, feeds entries into the split checker, accumulates accurate region size/key counts for whole-region scans, and optionally builds bucket split keys.
- For `CheckPolicy::Approximate`, the runner asks the host for approximate split keys and approximate bucket keys. On approximate split failure, it falls back to scan mode.
- Valid split keys cause approximate metadata updates and `router.ask_split` with a source string based on split reason. Empty split keys increment ignore metrics.
- `Task::ApproximateBuckets` refreshes bucket metadata without producing split keys when region buckets are enabled.
- `Task::CompactedEvent` maps compaction-declined bytes back to affected regions through `RegionInfoProvider` and reports per-region declined bytes to the router.

State and persistence behavior:
- The worker itself keeps no durable state. It reads live engine/tablet data and emits router updates.
- Bucket metadata state is held by raftstore through `refresh_region_buckets`; `BucketStatsInfo` defines how in-memory bucket stats should update, split, merge, version, and report deltas.
- `BucketStatsInfo::set_bucket_stat` preserves report deltas across metadata replacement and keeps `last_bucket_version` when buckets are cleared.
- Exact scan mode updates approximate size/key metadata with measured values only for whole-region scans, not request subranges.

Dependencies and integration points:
- Depends on coprocessor split checker implementations through `CoprocessorHost::new_split_checker_host` and `SplitCheckerHost`.
- Uses `engine_traits` iterators, tablet registry, compaction event traits, CF lists, and range property helpers.
- Uses PD bucket types (`BucketMeta`, `BucketStat`) and `pdpb::CheckPolicy`/`SplitReason`.
- Integrates with store FSM/peer code that schedules split checks after size/key threshold changes, admin split requests, bucket refreshes, and compaction events.

Risks and edge cases:
- Incorrect key encoding is dangerous: raw request ranges are encoded with transaction `Key` plus `keys::data_key`/`data_end_key`; whole-region ranges use encoded region bounds.
- Bucket update code assumes matching bucket/range lengths for partial refresh and can assert if violated.
- Scan mode can be expensive; it uses no cache fill and load-balance I/O type, but still traverses large CF data.
- Approximate mode must sanitize keys via `strip_timestamp_if_exists` and `is_valid_split_key`; invalid or unordered keys are skipped.
- Compaction declined-byte attribution depends on region info lookup and an empirical `region_split_check_diff / 16` threshold.

Test signals:
- Bucket tests cover version retention, bucket initialization, report-delta reset, split/merge metadata changes, flow preservation across bucket metadata changes, and report behavior.
- Split checker behavior is heavily exercised from coprocessor split check tests in size/key/table/half modules that instantiate `SplitCheckRunner` and schedule `SplitCheckTask`.
