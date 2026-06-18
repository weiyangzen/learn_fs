# sources/storage-engines/tikv/src/storage/raw/encoded.rs

## Purpose
This file adapts a raw snapshot whose stored keys and values use an `api_version::KvFormat` encoding into the plain raw-storage `Snapshot` interface expected by scan/get callers. It decodes raw values, filters expired TTL values, hides tombstones, and exposes user values through a wrapping iterator.

## Important APIs, Types, and Functions
- `RawEncodeSnapshot<S, F>` wraps an inner `Snapshot`, captures `ttl_current_ts()` once, and carries the selected `KvFormat`.
- `map_value` decodes an owned raw value and returns only valid, non-expired user data.
- `get_key_ttl_cf` returns remaining TTL for a key in a CF.
- The `Snapshot` implementation delegates bounds and extension access to the inner snapshot, and returns `RawEncodeIterator`.
- `RawEncodeIterator<I, F>` wraps an engine iterator and filters invalid values on movement.
- `find_valid_value` loops forward or backward until the iterator is invalid, errored, or points at a valid raw value.
- `Drop` records skipped invalid values in `RAW_VALUE_TOMBSTONE`.
- `MetricsExt` exposes RocksDB perf-context counters via `RawEncodeIterMetricsCollector`.

## Control Flow
Point reads call the inner snapshot, then `map_value`. Iteration calls inner movement methods first, then `find_valid_value`, which decodes each candidate and skips expired or deleted values in the requested direction. `value()` decodes the current raw value and returns the embedded `user_value`.

## State and Persistence Behavior
This wrapper does not persist anything. It interprets persisted raw values encoded by the selected `KvFormat`. The captured `current_ts` makes expiration checks stable for the lifetime of a snapshot/iterator. `skip_invalid` is transient accounting and is flushed to `RAW_VALUE_TOMBSTONE` on iterator drop.

## Dependencies and Integration Points
It depends on `api_version::KvFormat`, `engine_traits`, `raw_ttl::ttl_current_ts`, and storage `Snapshot`/`Iterator` traits. `RawStore` uses it for API V1 TTL and API V2 raw paths. API V2 composes it on top of `RawMvccSnapshot`.

## Risks
`value()` uses `unwrap()` on decode, so corrupt encoded values or misuse on an invalid iterator can panic. Because `current_ts` is captured once, very long scans may return values that expire during the scan. Tombstone-heavy ranges can cost more than callers expect.

## Test Signals
There are no tests in this file, but `raw_mvcc.rs` tests exercise `RawEncodeSnapshot<ApiV2>` layered over MVCC raw data. Coverage should include TTL expiry, tombstones, forward/reverse filtering, key-only scans, and malformed value handling.
