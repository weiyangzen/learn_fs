# sources/storage-engines/tikv/src/storage/raw/raw_mvcc.rs

## Purpose
This file adapts API V2 raw MVCC data, where multiple timestamped internal keys can exist for one user key, into a raw snapshot that exposes only the latest version per user key. It is intentionally one-directional per iterator positioning mode to avoid ambiguous movement across version groups.

## Important APIs, Types, and Functions
- `RawMvccSnapshot<S>` wraps an inner `Snapshot`.
- `seek_first_key_value_cf` performs a prefix seek over a timestamped key range and returns the first value, which is the latest version because timestamps are descending-encoded.
- The `Snapshot` implementation routes point reads through `seek_first_key_value_cf` and wraps iterators in `RawMvccIterator`.
- `RawMvccIterator<I>` stores an inner iterator plus optional cached current key/value for reverse iteration.
- `is_user_key_eq` compares encoded timestamped keys by truncated user key.
- `move_to_prev_max_ts` walks backward through a version group and caches the first/latest version for the previous user key.
- `next` skips all remaining versions of the current user key in forward scans.
- `MetricsExt` forwards RocksDB perf counters via `RawMvccIterMetricsCollector`.

## Control Flow
Forward scans seek to the first internal key for the requested user-key range and use `next` to skip over all versions sharing the same user key. Reverse scans call `seek_for_prev` or `seek_to_last`, then `move_to_prev_max_ts` backs up until it finds the max-timestamp entry for the previous user key, caching the key/value. Switching scan direction after positioning returns an error.

## State and Persistence Behavior
No writes occur. The wrapper interprets persisted API V2 raw keys, which include timestamps, and exposes one visible value per user key. It uses iterator upper bounds for point reads and transient buffers for reverse-scan cached key/value. Large cached buffers are shrunk when capacity is excessive.

## Dependencies and Integration Points
It depends on `txn_types::Key` timestamp encoding, `TimeStamp::zero`, `engine_traits::DATA_KEY_PREFIX_LEN` and `IterOptions`, and storage `Snapshot`/`Iterator` traits. `RawStore::V2` composes `RawMvccSnapshot` under `RawEncodeSnapshot<ApiV2>`.

## Risks
The iterator assumes timestamped key encoding and descending timestamp order. Direction switching is explicitly unsupported and produces an error. `is_user_key_eq` unwraps timestamp truncation, so invalid encoded keys can panic. Point-read bounds are sensitive to data-key prefix length and timestamp encoding.

## Test Signals
`test_raw_mvcc_snapshot` writes multiple API V2 timestamped raw versions, wraps the engine snapshot in `RawMvccSnapshot` and `RawEncodeSnapshot`, then verifies point reads, forward scan order, reverse scan order, and that two-way direction use is rejected.
