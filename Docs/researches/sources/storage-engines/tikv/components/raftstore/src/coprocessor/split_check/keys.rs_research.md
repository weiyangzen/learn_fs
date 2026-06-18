# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/keys.rs

## Purpose
`keys.rs` implements key-count-based split checking. It updates approximate key counts, decides whether a region needs split checking, and produces split keys either by scan counting commit-version entries or by engine approximate range properties.

## Important APIs, Types, And Functions
`Checker` tracks `max_keys_count`, `split_threshold`, `current_count`, accumulated `split_keys`, `batch_split_limit`, and `policy`. `KeysCheckObserver<C>` owns a `StoreHandle` router. `get_region_approximate_keys` calls `KvEngine::get_range_approximate_keys` over encoded region bounds.

## Control Flow
`KeysCheckObserver::add_checker` first asks the engine for an approximate key count up to `region_max_keys * batch_split_limit`. On success it sends `UpdateApproximateKeys`, records `REGION_KEYS_HISTOGRAM`, and adds a scan checker only if the count is at least `region_max_keys`. On approximate-stat error it logs and adds a checker anyway.

During scanning, `Checker::on_kv` ignores entries that are not commit versions. After `current_count` exceeds `split_threshold`, it records the current origin key and resets the counter. Scanning can stop early once the batch split limit is reached and the remaining counted tail is large enough. `split_keys` drops the final key if the last region fragment would be under `max_keys_count`. Approximate mode estimates how many split keys are needed with `calc_split_keys_count` and retrieves that many approximate split keys through the size module helper.

## State And Persistence Behavior
Only per-run counters and split keys are stored. Persistent raftstore state is updated indirectly via `StoreHandle::update_approximate_keys` and later split scheduling. Approximate counts are observability/control-plane inputs, not durable state in this file.

## Dependencies And Integration Points
Uses `engine_traits::KvEngine`, `kvproto::CheckPolicy`, split-check host/config, shared metrics, `StoreHandle`, and `size::get_approximate_split_keys`. It runs after size checking in the default registry, and comments rely on size checker ordering for bucket-scan reuse.

## Risks
Correctness depends on `KeyEntry::is_commit_version`; non-MVCC or unusual entries can affect counts. Approximate key counts may undercount subregions depending on range properties. The final split-key pop logic protects against undersized trailing regions but makes boundary behavior sensitive to off-by-one changes in threshold comparison.

## Test Signals
Tests cover scan split generation at configured key thresholds and batch limits, approximate-key split mode, approximate key counting from write/default CF data, split-key count math, interaction with bucket-enabled size checks, sub-region approximate-key behavior, and safe behavior when the receiver is dropped.
