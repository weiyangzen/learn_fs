<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/lib.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/lib.rs

## Purpose
Defines the public top-level API for S3 Select query handling: module exports, shared `QueryResult`, structured `QueryError`, and `ResolvedTable`.

## Important APIs, types, and functions
- Public modules: `object_store`, `query`, and `server`.
- `QueryResult<T>` aliases `Result<T, QueryError>`.
- `QueryError` variants cover DataFusion, not implemented features, multiple SQL statements, dispatcher build failures, cancellation, parser errors, missing/existing UDFs, and store errors.
- `From<DataFusionError>` preserves embedded `QueryError` values from `DataFusionError::External`.
- `ResolvedTable` wraps a table/path string and implements `table()` and `Display`.

## Control flow
Error conversion checks whether a DataFusion external error already contains a `QueryError`; if so it unwraps and returns it, avoiding double wrapping. All other DataFusion errors are boxed with caller location and SNAFU backtrace. `ResolvedTable` is a simple value object used by query planning/resolution code.

## State and persistence behavior
No persistent state is stored. `QueryError` captures diagnostic state, including optional backtrace/location for DataFusion failures. `ResolvedTable` stores the resolved table path/name as an owned string.

## Dependencies and integration points
Depends on `datafusion` error/parser types, `snafu`, and standard `Display`. The exported modules connect this top-level API to object-store access, query execution, and S3 Select server responses.

## Risks and edge cases
The `From<DataFusionError>` implementation unwraps a downcast after checking it, which is safe only if the external error is not concurrently changed, but the pattern is still brittle around type erasure. `MultiStatement` enforces a single-statement contract, which callers must preserve before dispatch. Error display text is part of test expectations and may leak to clients.

## Test signals
Tests cover display strings for major `QueryError` variants, conversion from DataFusion plan errors, parser error formatting, `ResolvedTable::table`, display, clone, equality, and inequality.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/lib.rs -->
