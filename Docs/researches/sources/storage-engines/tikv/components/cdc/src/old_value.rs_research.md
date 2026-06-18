# sources/storage-engines/tikv/components/cdc/src/old_value.rs

## Purpose
`old_value.rs` provides CDC old-value retrieval for MVCC changes. It combines an LRU cache populated from observed transaction extras with direct MVCC scans over the write/default column families when the cache misses.

## Important APIs, Types, and Functions
- `OldValueCallback` is the callback signature passed from observer batches into endpoint handling.
- `OldValueCacheSizePolicy` accounts cache capacity using encoded key length, `OldValue::size`, and mutation-type metadata.
- `OldValueCache` wraps `LruCache<Key, (OldValue, Option<MutationType>)>` and tracks access, miss, miss-none, and update counters; `resize` and `flush_metrics` synchronize Prometheus gauges/counters.
- `get_old_value` is the main lookup path: consume cache entry if present, otherwise append `query_ts`, build a write cursor, and call `near_seek_old_value`.
- `near_seek_old_value` scans MVCC write records for the latest visible value at or before the requested timestamp and optionally loads large values from the default CF via snapshot get or reusable cursor.
- `OldValueCursors` bundles reusable write/default cursors for scan-heavy paths.

## Control Flow
Cache hits are removed from the LRU and interpreted by mutation type. Inserts guarantee no previous value; puts/deletes may carry no value, inline value bytes, or a `ValueTimeStamp` requiring a default-CF read. Cache misses truncate the timestamp from the encoded key, append the query timestamp, and seek write CF. `near_seek_old_value` skips rollback/lock writes, honors GC fence visibility for puts, returns `None` for deletes or invisible puts, and loads long values through `near_load_data_by_write` or `get_cf_opt`.

## State and Persistence Behavior
The cache is in-memory and bounded by byte size. Metrics expose configured quota, current bytes, length, access/miss counts, and miss-none counts. Persistent state remains in MVCC RocksDB column families; this module only reads snapshots/cursors and never mutates engine data.

## Dependencies and Integration Points
The module depends on TiKV storage cursors, engine traits (`CF_WRITE`, `CF_DEFAULT`, `ReadOptions`), txn-types MVCC key/write encodings, TiKV LRU utilities, and CDC metrics. It is invoked through observer-created callbacks during endpoint event conversion.

## Risks and Edge Cases
Timestamp encoding assumptions are pervasive (`split_on_ts_for`, `decode_ts_from`, `truncate_ts` unwraps). Cache entries for `Unspecified` and `SeekWrite` are unreachable by contract. Correct GC fence handling is critical or CDC could emit stale old values. Cursor range bounds intentionally avoid accidental region-bound misuse.

## Test Signals
Tests validate cache resizing and eviction, old-value behavior across prewrite/commit/delete/rollback/pessimistic locks, GC fence visibility, cursor reuse statistics, prefix seek block-read reduction, and capacity enforcement when oversized values are inserted.
