# sources/object-store/rustfs/crates/s3select-query/src/dispatcher/mod.rs

## Purpose
This module declares dispatcher submodules.

## Important APIs, Types, And Functions
It exports `pub mod manager` and keeps `parquet_table` private to the dispatcher implementation.

## Control Flow
No local logic exists. Consumers use `dispatcher::manager` for `SimpleQueryDispatcher`.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
The private parquet table module is used by `manager` to support S3 Select parquet inputs.

## Risks And Edge Cases
External callers cannot use `ParquetSelectTable` directly because the module is private; this keeps surface area small but limits reuse.

## Test Signals
No local tests. Dispatcher behavior is covered in manager and integration tests.
