# sources/storage-engines/tikv/components/tidb_query_datatype/src/error.rs

## Purpose
This file defines datatype-definition errors that are separate from runtime codec/expression errors.

## Important APIs, types, and functions
`DataTypeError` is a `thiserror::Error` enum with `UnsupportedType { name }`, `UnsupportedCollation { code }`, and `UnsupportedCharset { name }`. Display messages are stable and human-readable.

## Control flow
No control flow exists beyond enum construction by callers such as `EvalType::try_from`, `Collation::from_i32`, and `Charset::from_name`.

## State and persistence behavior
The enum owns only the unsupported value details. There is no persistence or global state.

## Dependencies and integration points
It depends on `thiserror` and is re-exported from `tidb_query_datatype`. It is used where field metadata cannot be translated into supported TiKV execution semantics.

## Risks and edge cases
The error type is intentionally narrow. Callers needing richer context, such as source expression or column ID, must wrap or augment it at a higher layer.

## Test signals
Indirect tests in field and eval type modules assert that unsupported cases produce errors.
