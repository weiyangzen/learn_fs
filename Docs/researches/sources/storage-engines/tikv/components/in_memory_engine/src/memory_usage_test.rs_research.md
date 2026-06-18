# sources/storage-engines/tikv/components/in_memory_engine/src/memory_usage_test.rs

## Purpose

This file contains ignored, heavy memory amplification tests for representative TiDB index records stored in the in-memory engine write CF. It is not part of normal daily CI; the file documents a manual release-mode command and prints allocator deltas so maintainers can estimate resident memory overhead versus logical row/index payload size.

## Important APIs, Types, And Functions

- `Case` describes one benchmark case: name, encoded key, optional write value, logical bytes per key, and total logical target size.
- `test_memory_usage_two_fields_secondary_index_two_fields_clustered_index` builds a secondary-index style key with no value and a 29-byte logical payload assumption.
- `test_memory_usage_two_fields_unique_index_two_fields_clustered_index` builds a unique-index style write record with an encoded common-handle value.
- `evaluate_memory_usage` performs the actual population loop, reads allocator stats with `tikv_alloc::fetch_stats`, and reports amplification ratios.

## Control Flow

Each ignored test prepares a real encoded key/value case, then calls `evaluate_memory_usage`. The evaluator creates a test skiplist engine via `new_skiplist_engine_for_test`, captures starting allocator stats, repeatedly appends a unique MVCC timestamp to the key, encodes a `Write::new(WriteType::Put, commit_ts, value)` payload, and inserts it into `CF_WRITE`. After enough records approximate the configured logical total, it captures end allocator stats and prints resident-memory amplification plus per-allocator-stat deltas.

## State And Persistence Behavior

All state is in-memory skiplist state. No RocksDB persistence is used, and the test explicitly drops the skiplist after printing results. Memory accounting depends on allocator resident stats rather than engine metadata, so results are process- and allocator-sensitive.

## Dependencies And Integration Points

The test depends on `engine_traits::CF_WRITE`, `txn_types::{Key, Write, WriteType}`, `tikv_util::config::ReadableSize`, `hex`, `tikv_alloc`, and `crate::prop_test::new_skiplist_engine_for_test`. It integrates with the in-memory engine through its CF handle and with the internal key/value memory controller wrapper supplied by the property-test helper.

## Risks And Edge Cases

The tests are deliberately ignored because they insert about 200 MiB of logical data and rely on allocator resident statistics, which can vary by platform, build mode, allocator fragmentation, and other threads. The secondary-index and unique-index examples are hard-coded snapshots of TiDB encoding expectations; if upstream key/value formats change, the amplification scenario may become stale. The loop includes index `0..=logical_size_in_total / logical_size_pre_key`, so it intentionally overshoots the logical target by one record.

## Test Signals

The file itself is test-only. Its useful signal is manual printed amplification, not pass/fail assertions beyond successful insertion and allocator-stat lookup. It complements unit/property tests by measuring operational memory behavior for realistic key shapes.
