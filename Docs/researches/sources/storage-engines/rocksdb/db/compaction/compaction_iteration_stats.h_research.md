# sources/storage-engines/rocksdb/db/compaction/compaction_iteration_stats.h

## Purpose

This header defines `CompactionIterationStats`, a plain statistics accumulator used while iterating compaction input records. It groups counters for dropped records, input records/bytes, SingleDelete diagnostics, blob reads/relocations, and TimedPut preferred-sequence-number handling.

## Important Fields

Drop/filter counters:

- `num_record_drop_user`: records removed by user compaction filter decisions, excluding `kRemoveAndSkipUntil` skipped records.
- `num_record_drop_hidden`: records hidden by newer versions.
- `num_record_drop_obsolete`: obsolete records dropped.
- `num_record_drop_range_del`: point records dropped by range deletion.
- `num_range_del_drop_obsolete`: obsolete range deletions dropped.
- `num_optimized_del_drop_obsolete`: deletions obsoleted before bottom level due to file-gap optimization.
- `total_filter_time`: accumulated compaction filter time.

Input counters:

- `num_input_records`, `num_input_deletion_records`, `num_input_corrupt_records`.
- `total_input_raw_key_bytes`, `total_input_raw_value_bytes`.

Diagnostics:

- `num_single_del_fallthru` and `num_single_del_mismatch` track exceptional SingleDelete behavior.
- `num_blobs_read`, `total_blob_bytes_read`, `num_blobs_relocated`, `total_blob_bytes_relocated` track blob handling during compaction.
- `num_input_timed_put_records` and `num_timed_put_swap_preferred_seqno` track `kTypeValuePreferredSeqno` handling.

## Control Flow and State Behavior

The struct has no methods and no constructor logic beyond in-class zero initialization. Compaction iterator/job code can allocate it by value and increment fields as records are consumed, filtered, dropped, or rewritten. It has no persistence behavior on its own; callers decide how to export the counters into internal stats, event listeners, logs, or job info.

## Dependencies and Integration Points

The header only includes `<cstdint>` and `rocksdb/rocksdb_namespace.h`. It is intentionally lightweight so compaction iterator code can include it without pulling in DB internals. Its counters correspond to compaction filter decisions, merge/input scanning, range deletion handling, blob-file processing, SingleDelete semantics, and TimedPut record handling.

## Risks and Edge Cases

- A TODO notes input stats are incomplete because they do not include everything consumed by `MergeHelper`.
- Counter type choices vary between signed `int64_t` drop counters and unsigned `uint64_t` input/blob diagnostics; callers should avoid underflow and preserve semantics when aggregating.
- Because the struct is passive, missing increments in compaction code are easy to introduce and hard to catch without targeted stats tests.

## Test Signals

This header has no direct tests in the researched set. Indirect signals come from compaction tests and any assertions on compaction statistics, job info, blob GC counters, SingleDelete diagnostics, or TimedPut behavior elsewhere in RocksDB.
