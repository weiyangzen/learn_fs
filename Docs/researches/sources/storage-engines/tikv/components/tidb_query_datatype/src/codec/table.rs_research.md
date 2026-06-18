# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/table.rs

## Purpose
This file implements TiDB table and index key/value codec helpers for TiKV query components. It defines the raw key layout constants for table prefixes, record keys, index keys, extra system column IDs, and index value metadata flags. It also provides row encoding/decoding, row cutting for column pruning, index key cutting, table range validation, and the `RowHandle` abstraction used by executors such as index lookup.

## Important APIs, types, and functions
The table prefix shape is `t{table_id}_{r|i}` with comparable-encoded signed IDs. `extract_table_prefix`, `check_table_ranges`, `check_record_key`, `check_index_key`, and `decode_table_id` validate and decode this layout. `encode_row_key`, `encode_common_handle`, `encode_column_key`, and `encode_index_seek_key` construct raw TiDB keys for table rows, common handles, row columns, and index seeks.

`flatten` and private `unflatten` bridge logical datum types with storage encodings: durations become nanoseconds, time-like values become packed integers, floats round through `f32`, and unsupported enum/set/bit unflattening is rejected in this path. `encode_row`, `decode_col_value`, and `decode_row` implement row value conversion around `Datum` streams and `ColumnInfo`.

`RowColMeta` and `RowColsDict` are lightweight views over encoded row bytes. `cut_row` dispatches row v1/v2 handling: v1 scans datum pairs and records offsets; v2 uses `row::v2::RowSlice` plus `V1CompatibleEncoder` to emit v1-compatible column datums for requested columns. `cut_idx_key` maps requested index column IDs to encoded datum slices and optionally decodes a trailing int handle.

`RowHandle` abstracts lookup handles. `IntHandle` extracts one decoded integer handle column, builds row keys, emits prefix-next point range ends, and detects consecutive handles. `CommonHandle` consumes `LazyBatchColumnVec` extra common-handle keys, appends raw common-handle bytes to record prefixes, and returns a point range end by appending `0`.

## Control flow
Validation first checks fixed bytes and lengths, then decodes table IDs or handles. Row encoding interleaves `col_id, value` pairs and uses a single `Null` datum for empty rows. Row decoding decodes the whole datum stream, validates even pair counts, then only materializes requested columns. Row cutting avoids full materialization by recording offsets into the source buffer or by converting row v2 selected columns into a v1-compatible buffer.

Index key decoding skips `PREFIX_LEN + ID_LEN`, decodes one datum per `ColumnInfo`, and unflattens according to column type. `cut_idx_key` similarly skips the prefix and index ID, splits fixed index datums, then treats remaining bytes as an optional int handle.

## State and persistence behavior
The module does not persist data itself. State is carried in byte buffers, offset maps, and `EvalContext` warnings/errors during type conversion. `RowColsDict` owns encoded bytes and offset metadata, so callers can hold borrowed column slices safely as long as the dict lives. `CommonHandle::from_lazy_batch_column_vec` mutates the batch by taking extra handle keys, which is a one-shot transfer.

## Dependencies and integration points
The codec depends on `codec::prelude` numeric encoding, `Datum` encoding, `ColumnInfo`/`FieldType`, row v2 codecs, `EvalContext`, and `LazyBatchColumnVec`. Executors use `RowHandle` for table lookup planning. Table scans and coprocessor range checks use key validation helpers. TiDB compatibility is encoded through special negative column IDs, row v1/v2 compatibility, common-handle support, and collation/restored-data flags defined elsewhere.

## Risks and edge cases
`FieldTypeTp::Enum`, `Set`, and `Bit` are not supported by `unflatten`, despite related eval paths existing elsewhere. `decode_index_key` assumes the key is long enough to skip prefix and index ID; callers must supply valid index keys. `cut_row` notes that mismatched `col_ids` and `cols` give undefined results. `IntHandle::is_next_of` can overflow on `i64::MAX + 1` in debug builds if called with max previous handle. Common-handle point range end by appending `0` is a prefix range, not a consecutive-key optimization.

## Test signals
Tests cover row and index key round trips, row encode/decode/cut behavior, empty rows, table prefix extraction, table range validation, table ID decoding, key type checks, `IntHandle` extraction and type validation, point range end generation, and common-handle extraction/error cases. The tests also cover row v1 cut behavior and lazy batch column decoding assumptions.
