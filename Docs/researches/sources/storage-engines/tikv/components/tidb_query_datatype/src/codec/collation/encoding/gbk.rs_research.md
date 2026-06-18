# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gbk.rs

## Purpose
Implements GBK charset decode/encode and GBK-specific upper/lower transforms.

## Important APIs, Types, And Functions
`EncodingGbk` implements `Encoding::decode`, `encode`, `lower`, and `upper`. It delegates charset conversion to `encoding_rs::GBK` and case mapping to `unicode_letter` with MySQL worklog exceptions.

## Control Flow
`decode` calls `decode_without_bom_handling_and_without_replacement`, returning a UTF-8 byte vector on success and `cannot_convert_string` on invalid GBK. `encode` validates input as UTF-8 and uses `GBK.encode`. `lower` and `upper` iterate over Unicode chars, keep selected code points unchanged, otherwise apply `unicode_to_lower` or `unicode_to_upper`, then write UTF-8 bytes via `BytesWriter`.

## State And Persistence
No state is stored; all behavior is stateless conversion over input slices.

## Dependencies And Integration Points
Depends on `encoding_rs::GBK`, `BytesWriter`, `BytesGuard`, and shared Unicode case helpers. It is exported from `encoding/mod.rs` and selected by charset template macros.

## Risks
`GBK.encode` replacement behavior must be acceptable for callers because encode does not surface an error for unrepresentable chars. The hard-coded case exceptions must match TiDB/MySQL exactly.

## Test Signals
No local tests; coverage is expected through charset conversion and string function tests.
