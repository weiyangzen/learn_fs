# sources/storage-engines/tikv/components/tidb_query_executors/src/index_scan_executor.rs

## Purpose
`index_scan_executor.rs` implements `BatchIndexScanExecutor`, the batch executor that scans TiDB index key/value records from a `Storage` implementation and exposes index columns, handles, partition ids, and physical table ids as `LazyBatchColumnVec` batches. It is a thin public wrapper around the generic `ScanExecutor<S, IndexScanExecutorImpl, F>` plus a large `IndexScanExecutorImpl` responsible for TiDB index-value format decoding.

The executor supports old and newer index encodings, unique and non-unique indexes, int handles and common handles, local and global indexes, V1/V2 partition-id placement, old collation data, restored-data formats from TiDB 4.0/5.0, and optional `extra_common_handle_keys` needed by higher-level common-handle paths.

## Important APIs, Types, and Functions
- `BatchIndexScanExecutor<S, F>(ScanExecutor<...>)`: public batch executor exported by the crate. It delegates all `BatchExecutor` methods to `ScanExecutor`.
- `BatchIndexScanExecutor::check_supported`: validates pushed-down `IndexScan` column metadata through `check_columns_info_supported`.
- `BatchIndexScanExecutor::new`: derives schema and handle/partition layout from `ColumnInfo`, creates `IndexScanExecutorImpl`, and wires it into `ScanExecutor::new` with `ExecutorName::batch_index_scan`.
- `DecodeHandleStrategy`: selects `NoDecode`, `DecodeIntHandle`, or `DecodeCommonHandle`.
- `IndexScanExecutorImpl`: stores `EvalContext`, output schema, index-column ids, common-handle column ids, partition/physical-table-id column counts, cached `index_version`, and the `fill_extra_common_handle_key` flag.
- `ScanExecutorImpl` implementation: supplies `schema`, `mut_context`, `build_column_vec`, and `process_kv_pair`.
- Decoding helpers: `decode_int_handle_from_value`, `decode_int_handle_from_key`, `decode_int_handle_and_partition_from_key`, `extract_columns_from_row_format`, `extract_columns_from_datum_format`, `restore_original_data`, `get_index_version`, `process_old_collation_kv`, `process_kv_general`, `build_operations`, `decode_index_columns`, `decode_handle_columns`, `process_physical_table_id_column`, `decode_pid_columns`, `split_common_handle`, `split_partition_id`, and `split_restore_data`.

## Control Flow
Construction first inspects the tail of `columns_info`. `EXTRA_PHYSICAL_TABLE_ID_COL_ID` must be last if present, `EXTRA_PARTITION_ID_COL_ID` must precede it, and an int handle column must precede those special columns. `primary_column_ids_len` determines whether common-handle decoding is needed. The constructor rejects the invalid case where both int and common handles are pushed down, computes normal index column ids and common-handle column ids, then creates a `ScanExecutor` configured with direction, ranges, point-range acceptance for unique probes, and scanned-range awareness.

At execution time, `ScanExecutor` calls `IndexScanExecutorImpl::build_column_vec` to allocate raw columns for index columns, decoded `Int` columns for int handles and special ids, and raw columns for common-handle components. `process_kv_pair` validates the index key, strips the table/index prefix to get `key_payload`, lazily detects the index encoding version from the first value, and routes to either `process_kv_general` for new/extensible encodings or `process_old_collation_kv` for short legacy values.

The legacy path decodes indexed columns from the key payload first. For int handles, it uses the value when the remaining key payload is empty, otherwise parses the handle from the key and may also extract a partition id prefix. For common handles, it decodes the remaining key payload into the common-handle columns and optionally records the raw common handle. Partition id and physical table id output columns are filled either from the parsed global-index partition id or by falling back to the table id encoded in the key prefix.

The general path first calls `build_operations`. That routine uses `tail_len`, `index_version`, common-handle flag segments, partition-id segments, and restore-data segments to produce high-level operations. It prefers partition id from value for backward compatibility, otherwise falls back to partition id from key for V2 global index values. Then `process_kv_general` writes the physical table id or partition id columns, decodes normal index columns, and decodes handle columns. For TiDB 4.0 restore data it decodes all index columns from row-format restore data. For TiDB 5.0 restore data it decodes sort-key datums first and then `restore_original_data` reconstructs original non-binary string values, including `_bin` padding restoration.

## State and Persistence Behavior
The executor is runtime-stateful but not persistently stateful. It owns an `EvalContext` that accumulates evaluation warnings/behavior during decoding. `index_version` is initialized to `-1` and cached after the first processed KV, so a single executor assumes a consistent value format across its scan. Output state is per batch in `LazyBatchColumnVec`; raw columns may be lazily decoded by parent executors. `extra_common_handle_keys` are appended per processed row when requested. Statistics, scanned ranges, storage stats, and cacheability are delegated to the inner `ScanExecutor`.

The source of persistent truth is the TiKV/TiDB encoded key/value bytes in storage. This file only interprets those bytes; it does not write storage data.

## Dependencies and Integration Points
- Integrates with `BatchExecutor` from `interface.rs` and with the generic scan machinery in `util::scan_executor`.
- Depends on `tidb_query_datatype` for datum encoding/decoding, row v2 decoding, table key helpers, collations, field type accessors, and lazy batch columns.
- Depends on `tidb_query_common::storage::Storage` and `kvproto::coprocessor::KeyRange` for scan input.
- Uses `api_version::KvFormat` and defaults the support-check type alias to `ApiV1`.
- Uses `tipb::{IndexScan, ColumnInfo, FieldType}` as the TiDB pushed-down plan contract.
- Exported from `lib.rs` as `BatchIndexScanExecutor`, so runner/planner code can instantiate it for pushed-down index scans.

## Risks and Edge Cases
- Column ordering is part of the wire contract. Normal index columns, common-handle columns, int handle, partition id, and physical table id must be ordered exactly as expected; wrong order can produce raw bytes that later fail schema decoding rather than failing construction.
- `index_version` is cached from the first KV. Mixed encodings in one scan would be risky because later rows reuse the initial version decision.
- `tail_len`, common-handle length, partition-id segment length, and remaining bytes are all corruption-sensitive. The code returns explicit errors for malformed tails, unexpected extra bytes, invalid handle flags, missing row-format columns, and mismatched common-handle mode.
- Global index support has compatibility complexity: V1 may carry partition id in both key and value, while V2 carries it only in the key. The implementation must return partition id for global physical-table-id columns instead of the index table id.
- Restore-data semantics depend on collation and column type. `_bin` string reconstruction combines key sort data with restored padding counts; non-binary collations use restored row data. Mistakes here produce semantically wrong string values while preserving sort order.
- `fill_extra_common_handle_key` is valid only when the decoded handle operation is `CommonHandle`; other operations are rejected.

## Test Signals
The in-file tests are extensive. `test_basic` covers normal and unique int-handle scans, reverse scans, prefix/point ranges, physical table id output, and wrong column order behavior. Common-handle tests cover unique and non-unique common handles, extra common handle keys, and global index partition id output. Collation tests cover char/varchar restoration for int handles and common handles across `_bin`, Unicode/general CI, and Latin1 binary cases. Global index tests cover V1/V2 partition-id placement, optional legacy partition columns, optional physical-table-id columns, malformed key handling, and the new-encoding V2 path through `process_kv_general`. `test_index_version` pins version detection.
