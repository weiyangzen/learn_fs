# sources/storage-engines/tikv/components/tidb_query_datatype/src/def/field_type.rs

## Purpose
This file provides Rust-side definitions and accessors for TiDB field metadata stored in protobuf `FieldType` and `ColumnInfo`. It centralizes MySQL/TiDB type codes, collation codes, charset parsing, field flags, and helper predicates used throughout expression evaluation, codecs, and executors.

## Important APIs, types, and functions
`FieldTypeTp` mirrors parser MySQL type constants, including TiDB-specific `TiDbVectorFloat32`. `from_i32`, `from_u8`, and `to_u8` convert between protobuf/raw numeric forms and enum values. `Collation` maps TiDB collation IDs, including legacy positive IDs and newer negative padding-aware IDs, into a smaller enum. `Collation::from_i32` treats unknown nonnegative codes as `Utf8Mb4BinNoPadding` for compatibility but rejects unknown negative codes. `Charset::from_name` parses known charset names.

`FieldTypeFlag` defines bitflags for not-null, unsigned, binary, parse-to-json, boolean literal, and enum/set-as-int behavior. `FieldTypeAccessor` abstracts over `tipb::FieldType` and `tipb::ColumnInfo`, exposing `tp`, `flag`, `flen`, `decimal`, and `collation` getters/setters plus semantic helpers like `is_hybrid`, `is_blob_like`, `is_char_like`, `is_varchar_like`, `is_string_like`, `is_binary_string_like`, `is_non_binary_string_like`, `is_unsigned`, `is_bool`, and `need_restored_data`.

## Control flow
Accessor implementations translate between differing protobuf field names: `FieldType` uses `tp`, `flag`, `flen`, `decimal`, and `collate`; `ColumnInfo` uses flattened `tp`, `flag`, `column_len`, `decimal`, and `collation`. Predicate helpers build on the accessors, so executor and codec code can work with either protobuf type.

## State and persistence behavior
The module mutates protobuf structs in-place through setter methods but maintains no global state. Flag conversion uses truncating bitflag parsing, so unknown flags are ignored by the accessor layer.

## Dependencies and integration points
The code depends on `tipb::{FieldType, ColumnInfo}` and local `DataTypeError`. It is used by row codecs, expression type inference, collation-aware comparison and aggregation, table scan schema construction, and index restored-data decisions.

## Risks and edge cases
`FieldTypeTp::from_i32` and `from_u8` use `unsafe transmute` after numeric range checks. This is concise but depends on the enum discriminants remaining exactly aligned with TiDB constants. `to_u8` always returns `Some`, even for values represented by negative or large `i32` after cast; current variants fit the intended byte space. `need_restored_data` has nuanced collation logic and is a compatibility-sensitive area, especially for varstrings and newer UTF8MB4 0900 collations.

## Test signals
Tests cover type numeric conversion, invalid ranges, u8 round trips, collation aliasing and rejection, charset parsing, and `need_restored_data` outcomes for binary, general, unicode, 0900, GBK, and GB18030 collations.
