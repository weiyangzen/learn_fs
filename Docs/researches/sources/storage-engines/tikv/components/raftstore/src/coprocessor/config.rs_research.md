# sources/storage-engines/tikv/components/raftstore/src/coprocessor/config.rs

## Purpose
This file defines raftstore coprocessor configuration for split checking, region bucket behavior, consistency checking, and online config dispatch. It also validates derived split and bucket thresholds, with raftstore-v2-specific optimization for much larger split size defaults.

## Important APIs, Types, and Functions
- `Config` is serializable/deserializable and derives `OnlineConfig`. It includes split-on-table, batch split limit, optional split/max size and key thresholds, consistency check method, deprecated perf level, bucket enablement/size/approximation/merge settings, and approximate-bucket preference.
- `ConsistencyCheckMethod` selects raw or MVCC consistency checking.
- Constants include `SPLIT_SIZE` (256 MB), `RAFTSTORE_V2_SPLIT_SIZE` (10 GB), `BATCH_SPLIT_LIMIT`, `DEFAULT_BUCKET_SIZE` (50 MB), and `DEFAULT_REGION_BUCKET_MERGE_SIZE_RATIO`.
- `Config::region_split_size`, `region_max_keys`, `region_max_size`, `region_split_keys`, and `enable_region_bucket` expose defaulted values.
- `Config::optimize_for(raftstore_v2)` sets default split size to the v2 value when appropriate.
- `validate_bucket_size()` enforces bucket-size, approximate-threshold, nonzero, and merge-ratio constraints.
- `Config::validate(raft_kv_v2)` fills missing derived thresholds, validates max >= split values, and auto-enables region buckets for raftstore-v2 when useful.
- `SplitCheckConfigManager<EK>` dispatches online config changes to a `Scheduler<SplitCheckTask<EK>>`.

## Control Flow
Validation first fills `region_split_keys`, then validates or derives `region_max_size` and `region_max_keys`. It then validates bucket settings. If bucket validation succeeds and raft-kv-v2 is enabled with unspecified `enable_region_bucket`, it auto-enables buckets when split size is at least twice bucket size. If bucket validation fails but buckets are disabled, the invalid bucket settings are tolerated.

## State and Persistence Behavior
The config object is mutable during validation: missing optional thresholds are materialized into `Some` values, and `enable_region_bucket` can be set. Online changes are not applied directly here; they are scheduled as `SplitCheckTask::ChangeConfig`.

## Dependencies and Integration Points
It depends on `engine_traits::KvEngine`, online-config traits, serde, TiKV `ReadableSize`, worker `Scheduler`, raftstore `SplitCheckTask`, and consistency-check config types. Raftstore-v2 tests use this config for bucket behavior.

## Risks and Edge Cases
- Validation mutates the config, so callers comparing pre/post config should expect derived values to appear.
- Invalid bucket size is accepted if bucket feature is disabled; enabling later without revalidation could be risky if not routed through config manager.
- The comment says region max size default is split size times 3/2; code implements `split / 2 * 3`, which is integer-sized `ReadableSize` arithmetic.
- `optimize_for()` only changes split size when it was unspecified.

## Test Signals
The in-file `test_config_validate()` covers max-size and max-keys validation/derivation, disabled bucket tolerance, and split-key derivation. Integration bucket tests in raftstore-v2 validate runtime effects of enabling buckets.
