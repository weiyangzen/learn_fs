<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/mvcc.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/properties/mvcc.rs

## Purpose
`properties/mvcc.rs` collects and decodes MVCC statistics for tirocks SST table properties. It supports TiDB/TxnKV write-CF keys and RawKV default-CF keys, tracks timestamp ranges, row/version counts, put/delete counts, row-version maxima, parse errors, and row index checkpoints.

## Important APIs, Types, and Functions
Constants define property keys such as `tikv.min_ts`, `tikv.max_ts`, `tikv.num_rows`, `tikv.num_puts`, `tikv.num_deletes`, `tikv.num_versions`, `tikv.max_row_versions`, and `tikv.rows_index`.

`MvccPropertiesCollector` implements tirocks `TablePropertiesCollector`. It stores collector name, accumulated `MvccProperties`, last logical row, parse-error count, current row-version count, current `PropIndex`, row indexes, key mode, and current TTL timestamp. `MvccPropertiesCollectorFactory::default` creates Txn collectors, while `rawkv` creates RawKV collectors. `encode_mvcc` and `decode_mvcc` serialize/deserialize properties.

`MvccPropertiesExt for RocksEngine::get_mvcc_properties_cf` reads table properties for a range, decodes MVCC metadata from each SST, filters files whose minimum timestamp is after the safe point, and combines the rest.

## Control Flow
Collector `add` accepts put and delete entry types only. It validates TiKV data keys, splits timestamp from encoded keys, updates min/max timestamps, and skips value parsing for RocksDB delete entries. For put entries, it increments version count, detects new logical rows by comparing the key without timestamp to `last_row`, updates row counts and max row versions, then classifies put/delete semantics.

RawKV mode decodes `ApiV2` raw values and uses TTL validity at collector creation time to classify live values as puts and expired/deleted values as deletes. Txn mode parses `WriteType` from the value and counts `Put` and `Delete`. Row index checkpoints are inserted for the first row and every `PROP_ROWS_INDEX_DISTANCE` rows.

`finish` inserts the final pending row index, encodes all MVCC fields, stores parse-error count, and encodes row indexes. `decode_mvcc` is backward-compatible for missing `num_deletes`, deriving it as `num_versions - num_puts`.

## State and Persistence Behavior
Collector state exists while building one SST. Encoded MVCC properties persist in SST metadata and are later used for range estimates, timestamp filtering, and GC/split decisions. Querying MVCC properties is read-only.

## Dependencies and Integration Points
It depends on `api_version`, TiKV key validation, `txn_types::{Key, TimeStamp, Write, WriteType}`, engine-trait `MvccProperties`, TTL current time, tirocks table-property collector APIs, and shared property codecs. `engine_iterator::TsFilter` relies on the same `tikv.min_ts`/`tikv.max_ts` names for table pruning.

## Risks and Edge Cases
Invalid keys or values increment `num_errors` but do not fail SST creation. RawKV mode currently uses `ApiV2` decoding explicitly; other raw formats would need separate handling. TTL classification depends on current time captured at collector creation, so long compactions around expiration boundaries can classify values relative to that instant. Delete entry types update min/max timestamp but not row/version counters. Row-index insertion logic is sensitive to sorted key order.

## Test Signals
Tests cover Txn MVCC properties with puts/deletes/delete entries, RawKV mode with valid/expired/delete raw values, and a benchmark for collector add loops. More tests should cover invalid data keys, malformed timestamps, malformed values, safe-point filtering across multiple SSTs, row index encoding, and missing legacy `num_deletes`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/mvcc.rs -->
