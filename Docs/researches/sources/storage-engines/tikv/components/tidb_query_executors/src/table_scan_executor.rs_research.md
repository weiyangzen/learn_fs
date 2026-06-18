# sources/storage-engines/tikv/components/tidb_query_executors/src/table_scan_executor.rs

## Purpose

`table_scan_executor.rs` implements `BatchTableScanExecutor`, the table row scan executor for TiKV coprocessor batch execution. It adapts the generic `ScanExecutor` to TiDB table row encodings, decodes row values into requested columns, fills primary key handle columns, supplies defaults for missing columns, and supports common handles plus special extra columns such as physical table id and commit timestamp.

## Important APIs, Types, and Functions

- `BatchTableScanExecutor<S, F>` wraps `ScanExecutor<S, TableScanExecutorImpl, F>` where `S: Storage` and `F: KvFormat`.
- `check_supported` delegates to `check_columns_info_supported`, currently validating primary-key handle eval types.
- `new` analyzes `ColumnInfo` descriptors, builds output schema via `field_type_from_column_info`, collects default values, maps column IDs to output indices, records handle indices, determines whether key-only scanning is sufficient, and configures `ScanExecutorOptions`.
- `TableScanExecutorImpl` stores `EvalContext`, schema, per-column defaults, `column_id_index`, `handle_indices`, `primary_column_ids`, and reusable `is_column_filled`.
- `process_v1` decodes old row format where value is datum-encoded column-id/value pairs.
- `process_v2` decodes row-v2 data through `RowSlice`, searching non-null and null column IDs and using `V1CompatibleEncoder` to write datum-compatible raw bytes.
- `build_column_vec` creates decoded integer columns for primary handles and special physical table/commit-ts columns, and raw columns for normal row data.
- `process_kv_pair` is the core row materializer for each scanned KV entry.

## Control Flow

At construction, non-PK requested columns are inserted into `column_id_index`, while PK-handle columns are recorded in `handle_indices`. `is_key_only` remains true only when all requested data can be derived from the key and no prefix common-handle/restored-data case requires the row value. `load_commit_ts` is enabled when `_tidb_commit_ts` is requested. `accept_point_range` is true only when there is no common handle.

For every batch, the generic scan wrapper calls `build_column_vec`, then calls `process_kv_pair` for each scanned KV. `process_kv_pair` first decodes value bytes if present. Row v2 and row v1 take separate decoding paths and push only requested columns, ignoring duplicate row-v1 column IDs after logging. Next, if integer PK handles are requested, it decodes the int handle from the key and pushes it to all handle output indices. If common-handle primary column IDs exist, it decodes each datum from the common handle and fills requested primary columns from key data. Otherwise it validates the record key.

After normal columns and handles, special extra columns are filled. `_tidb_rowid`-style physical table id is decoded from the key when requested. `_tidb_commit_ts` is pushed from the storage entry's commit timestamp; absence is an error if requested. Finally, every unfilled requested column gets its default value, NULL if nullable and no default exists, or an error if the column is NOT NULL and missing. Filled flags are reset for the next row.

## State and Persistence Behavior

The executor keeps no durable state. Per-instance persistent state consists of immutable schema/default/mapping metadata and a reusable `is_column_filled` vector. `EvalContext` accumulates warnings and is drained by the generic scan wrapper per result. Scan cursor progress, range awareness, storage statistics, and cacheability live in `ScanExecutor` and its `RangesScanner`.

## Dependencies and Integration Points

This file depends on `api_version::{ApiV1, KvFormat}`, TiDB row/table codecs, `kvproto::coprocessor::KeyRange`, `tidb_query_common::storage::Storage`, `smallvec` for handle indices, and `collections::HashMap`. It integrates with `util::scan_executor::ScanExecutor` for range scanning and `BatchExecutor` for batch pipeline semantics. It also integrates with storage commit timestamp loading and special TiDB column IDs from `tidb_query_datatype::codec::table`.

## Risks and Edge Cases

- Corrupted row data may partially fill columns before error. The generic scan executor truncates columns to equal length, but table decoding changes must preserve that contract.
- Missing NOT NULL data is treated as corruption and returns an error.
- Duplicate row-v1 column IDs are logged and ignored rather than aborting, which preserves availability but may hide upstream data issues.
- Common handle prefix columns can require restored data from row value rather than key-only scan; `is_key_only` calculation is sensitive to `primary_prefix_column_ids` and `need_restored_data`.
- Requesting `_tidb_commit_ts` requires storage to load commit timestamps; missing commit_ts is an error.
- Multiple PK handle columns or duplicate column IDs preserve only the last mapping in some cases as documented by comments.

## Test Signals

The tests are extensive. They cover point/range/mixed scans, varying column orders and PK positions, batch sizes, execution summary/scanned row stats, corrupted values, locked storage errors, multiple handle columns, common handles, prefix common-handle columns, restored data, and physical table id special columns. These tests validate drain behavior, partial rows on error, default value handling, raw versus decoded column representation, and schema/value alignment.
