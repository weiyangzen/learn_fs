# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/mod.rs

## Purpose
Defines the public chunk codec module surface.

## APIs, Flow, And State
The module declares `chunk` and `column`, re-exports `Chunk`, `ChunkEncoder`, `RowIterator`, `ChunkColumnEncoder`, and `Column`, and also re-exports codec `Error` and `Result`. There is no runtime state.

## Dependencies And Integration
Provides a stable import path for batch encoders, tests, and query datatype code needing chunk containers or chunk serialization helpers.

## Risks And Test Signals
Risk is limited to re-export churn. Downstream compile failures and chunk module tests signal issues.
