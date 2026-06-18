# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/encoder_for_test.rs

## Purpose
This test-only module builds row-format-v2 byte buffers for unit tests. It is intentionally straightforward and mirrors the TiDB row v2 layout: version, flags, non-null/null counts, sorted column IDs, offsets, values, and optional checksum bytes.

## Important APIs, Types, and Functions
`Column` carries a column id, `ScalarValue`, and `FieldType`, with builders for type, unsigned flag, and decimal precision. `Column::encode_for_checksum` serializes supported column values into the TiDB checksum input format. `ChecksumHandler` abstracts checksum calculation and metadata. `Crc32RowChecksumHandler` implements it with `crc32fast` and `ChecksumHeader`.

`RowEncoder` extends `NumberEncoder` with `write_row`, `write_row_with_checksum`, and `write_row_impl`. It sorts non-null columns and null IDs, chooses small or big format, writes IDs and offsets at the selected width, writes scalar values, and appends checksum header/value and optional extra checksum. `ScalarValueEncoder` writes compact v2 payloads for signed/unsigned integers, decimals, reals, bytes, datetime, duration, and JSON. `prepare_cols_for_test` supplies a representative row for checksum tests.

## Control Flow and State
`write_row_impl` scans input columns to determine whether any ID exceeds 255, separates null from non-null values, sorts by column ID, encodes non-null payloads while collecting end offsets, upgrades to big format if value bytes exceed `u16::MAX`, then emits the full row. Checksums are calculated before row encoding over sorted non-null columns. The checksum handler stores a reusable buffer and crc32 hasher state.

## Dependencies and Integration Points
The module depends on `codec::prelude`, `tipb::FieldType`, field accessor traits, `ScalarValue`, MySQL decimal/json/duration encoders, `EvalContext`, and `crc32fast`. It is used by row v2 tests and by v1 compatibility tests to create authoritative v2 payloads without relying on production TiDB encoders.

## Risks and Edge Cases
This module is test-only, so production safety risk is low, but its byte expectations influence codec compatibility tests. Unsupported scalar/type combinations return errors in checksum encoding and `write_value` uses `unreachable!()` for unsupported or null values after the caller has filtered nulls. IDs are cast to `u8` or `u32` based on the selected format, so invalid negative IDs would produce nonsensical bytes if introduced by a test.

## Test Signals
Tests assert exact encoded bytes for unsigned integer rows, mixed-type small rows, big rows with IDs above 255, and checksum rows with header version bits and optional extra checksum. They also verify checksum calculation against independently fed crc32 bytes.
