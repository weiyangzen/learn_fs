# sources/object-store/rustfs/crates/s3select-api/src/object_store.rs

## Purpose
This file adapts RustFS erasure-coded object storage to DataFusion's `object_store::ObjectStore` interface for S3 Select reads. It handles object metadata, ranged reads, S3 Select scan ranges, SSE-C read headers, CSV delimiter normalization, JSON DOCUMENT flattening to NDJSON, and test-only helpers for stream conversion.

## Important APIs, Types, And Functions
`EcObjectStore::new` resolves the global `ECStore`, detects multi-byte CSV field delimiters, and records whether JSON DOCUMENT mode needs whole-document flattening. `SelectScanRange` models inclusive S3 Select byte bounds. `scan_range_from_bounds` and `validate_scan_range_bounds` implement AWS-style validation, including suffix semantics for end-only ranges. The `ObjectStore` implementation supports `get_opts` and `get_ranges`; mutation, list, and copy operations intentionally return unsupported errors. `ConvertStream`, `DelimiterConverter`, `convert_field_delimiter_stream`, `scan_range_stream`, `json_document_ndjson_stream`, and `bytes_stream` are the main stream transformation helpers.

## Control Flow
`get_opts` builds `ObjectOptions` from DataFusion get options, loads object size when scan range context is needed, opens an `ECStore` reader with SSE-C headers and optional adjusted range, then selects a payload branch. Head requests return an empty stream. Explicit DataFusion ranges stream exactly the requested byte count. JSON DOCUMENT requests reject objects larger than `MAX_JSON_DOCUMENT_BYTES`, then lazily read the full object and parse in `spawn_blocking`. Scan-range CSV/JSON-line reads rewind by the record delimiter length, optionally prepend the CSV header record, and emit whole records whose start offset falls in the scan range. Multi-byte CSV field delimiters are converted to RustFS/DataFusion's default comma both in full-object and scan-range paths.

## State And Persistence Behavior
The adapter does not persist data. It holds an `Arc<SelectObjectContentInput>` and `Arc<ECStore>`, derives request-local flags, and streams bytes from the backing object. JSON DOCUMENT mode can allocate memory proportional to object size up to the 128 MiB cap. Scan-range state is kept in `ScanRangeState` with current object offset, pending record bytes, and queued output chunks.

## Dependencies And Integration Points
The file integrates `s3s` Select request DTOs, RustFS `ECStore` object readers, DataFusion/object_store abstractions, `tokio_util::ReaderStream`, `serde_json`, HTTP SSE-C headers, and `rustfs_common::DEFAULT_DELIMITER`. It is installed into `SessionCtxFactory` as the object store backing non-test S3 Select queries and is also used by parquet scan-range planning through `SelectScanRange`.

## Risks And Edge Cases
JSON sub-path extraction is a lightweight string parser over the SQL expression, so complex quoting, comments, or nested SQL syntax can diverge from the real SQL parser. JSON DOCUMENT fallback emits the whole root when the requested sub-path is missing, which may surprise callers expecting zero rows. `get_opts` only supports read paths; accidental DataFusion list/copy/delete calls surface as runtime unsupported errors. Scan ranges include records by record-start offset and must keep delimiter rewind logic synchronized with AWS S3 Select expectations. Multi-byte delimiter conversion is byte-based and does not understand CSV quoting. JSON DOCUMENT still buffers the full accepted object.

## Test Signals
The file has unit tests for delimiter replacement across chunks and EOF, scan-range record/header inclusion, multi-byte record delimiters, suffix and invalid scan range validation, bounded DataFusion range conversion, SSE-C header propagation, stream length limiting, JSON DOCUMENT flattening for arrays, objects, empty arrays, pretty JSON, nested values, invalid/empty input, sub-path fallback, and SQL sub-path extraction.
