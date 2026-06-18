# sources/object-store/rustfs/crates/s3select-api/src/query/execution.rs

## Purpose
This file defines query execution contracts, query output handling, phase timing metrics, and a lightweight query state machine for S3 Select.

## Important APIs, Types, And Functions
`PhaseTimer` records histogram metrics and debug logs on drop. `QueryType` distinguishes batch and stream execution, although the default is batch. `QueryExecution` exposes `start` and `cancel`. `Output` wraps either `StreamData(SendableRecordBatchStream)` or `Nil(())` and can return a schema, collect batches, expose the stream, count rows, or act as a `Stream<Item = Result<RecordBatch, QueryError>>`. `QueryExecutionFactory` creates executions from `Plan` plus `QueryStateMachineRef`. `QueryStateMachine` stores `SessionCtx`, `Query`, current `QueryState`, and start time, with phase transitions for analyze, optimize, and schedule.

## Control Flow
Execution implementations call `begin_*` and `end_*` methods around phases. `Output::chunk_result` collects DataFusion stream batches and synthesizes an empty batch with the correct schema when no batches arrive. The stream implementation forwards polling to DataFusion for `StreamData` and ends immediately for `Nil`.

## State And Persistence Behavior
State is in memory under a `parking_lot::RwLock`. `finish`, `cancel`, and `fail` only translate the state enum; TODOs indicate missing cleanup or side effects. Metrics record phase durations and timestamps but no durable query history is written.

## Dependencies And Integration Points
The file connects DataFusion Arrow and physical stream types with the RustFS query API. `SqlQueryExecution` implements the trait, and `DatabaseManagerSystem` returns `Output` through `QueryHandle`.

## Risks And Edge Cases
`affected_rows` casts `usize` to `i64`, with a comment noting overflow risk. `num_rows` suppresses collection errors by returning zero. `Output::into_record_batch_stream` rejects `Nil`, so callers need to branch on empty output. State transitions are not validated, so invalid sequences are possible. `finish` is not called by the current query execution path.

## Test Signals
No direct tests are in this file. Integration tests cover output collection, staged execution, limit row counts, and concurrent query execution.
