# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/error.rs

## Purpose
Defines the codec-layer error type and MySQL-compatible error codes used by TiKV query datatype encoding, decoding, conversion, and evaluation routines. It also maps these errors into protobuf and common evaluation error forms.

## Important APIs, Types, And Functions
- Error code constants for unknown errors, truncation, bad values, division by zero, data too long, regexp errors, timezone errors, zlib corruption, conversion failures, and overflow.
- `Error` enum: `InvalidDataType`, `Encoding`, `ColumnOffset`, `UnknownSignature`, `Eval`, `CorruptedData`, and boxed `Other`.
- Constructors: `overflow`, `truncated_wrong_val`, `truncated`, `m_bigger_than_d`, cast overflow helpers, timezone/division/data-too-long/conversion/datetime/zlib/parameter/regexp helpers.
- Inspectors: `code`, `is_overflow`, `is_truncated`, and `unexpected_eof`.
- Conversions into `tipb::Error`, `EvaluateError`, and from UTF-8, serde, parse-float, TiKV codec, IO, regexp, external codec, and datatype schema errors.
- `Result<T>` alias and `ErrorCodeExt` implementation.

## Control Flow
Most constructors format a MySQL-style message and wrap it in `Error::Eval` with the appropriate code. `code` returns the embedded eval code or `ERR_UNKNOWN` for structural errors. Conversion into `tipb::Error` copies the numeric code and rendered message. Conversion into `EvaluateError` preserves custom eval code/message but degrades non-eval errors into generic `Other` strings. `ErrorCodeExt` maps variants to TiKV error-code categories.

## State And Persistence Behavior
No mutable or persistent state. The persistence-facing behavior is serialized error propagation into `tipb::Error` and stable numeric MySQL/TiDB error codes.

## Dependencies And Integration Points
Used by nearly every codec submodule via `crate::codec::Result` and constructors. It integrates with `thiserror`, `error_code`, `tipb`, `tidb_query_common::error::EvaluateError`, regex/serde/codec error types, and scalar function signatures.

## Risks And Edge Cases
- Non-`Eval` variants collapse to `ERR_UNKNOWN` when converted to `tipb::Error`, so some structural failures may lose specific MySQL-style codes.
- Several external errors are boxed into `Other`, preserving text but not structured fields.
- `is_truncated` only checks `ERR_TRUNCATE_WRONG_VALUE`, not the `WARN_DATA_TRUNCATED` warning code returned by `truncated`.
- Error message compatibility matters because clients may compare TiDB/MySQL error strings.

## Test Signals
No local tests in this file. Indirect coverage comes from conversion, codec, regexp, time, and expression tests that assert error handling. Direct unit tests would be useful for code mappings, `tipb::Error` conversion, and warning-vs-error truncation distinctions.
