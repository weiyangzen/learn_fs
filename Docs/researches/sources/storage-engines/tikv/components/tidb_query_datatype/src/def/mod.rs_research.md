# sources/storage-engines/tikv/components/tidb_query_datatype/src/def/mod.rs

## Purpose
This module is the public facade for datatype definitions. It declares the `eval_type` and `field_type` submodules, re-exports their primary types, and defines shared MySQL/TiDB width constants.

## Important APIs, types, and functions
Exports include `EvalType`, `Charset`, `Collation`, `FieldTypeAccessor`, `FieldTypeFlag`, and `FieldTypeTp`. Constants include `UNSPECIFIED_LENGTH`, `MAX_BLOB_WIDTH`, `MAX_DECIMAL_WIDTH`, and `MAX_REAL_WIDTH`.

## Control flow
There is no runtime control flow; this is module organization and shared constant declaration.

## State and persistence behavior
The module has no state. Constants are compile-time values used by builders, codecs, and expression code.

## Dependencies and integration points
Consumers import this module through `tidb_query_datatype::{...}` or the crate prelude. It ties together the field metadata and eval type conversion modules for the rest of the query stack.

## Risks and edge cases
`MAX_BLOB_WIDTH` is an `i32` while neighboring constants are `isize`, with a FIXME noting the mismatch. New datatype definitions must be re-exported here if they are intended as public API.

## Test signals
There are no direct tests in this facade; coverage is supplied by `eval_type.rs`, `field_type.rs`, and downstream users.
