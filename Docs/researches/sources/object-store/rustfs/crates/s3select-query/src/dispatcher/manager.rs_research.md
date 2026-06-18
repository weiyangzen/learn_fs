# sources/object-store/rustfs/crates/s3select-query/src/dispatcher/manager.rs

## Purpose
This file implements the default query dispatcher. It creates sessions, registers the current object as a DataFusion table, parses SQL, rejects unsupported multi-statement/empty input, builds logical plans, and executes them through the execution factory.

## Important APIs, Types, And Functions
`SimpleQueryDispatcher` owns the request input, session factory, parser, execution factory, function manager, and table provider. Its `QueryDispatcher` implementation exposes one-shot and staged execution. `build_scheme_provider` creates either a `ParquetSelectTable` or a DataFusion `ListingTable` for CSV/JSON. `TrackedRecordBatchStream` wraps output streams. `SimpleQueryDispatcherBuilder` validates required dependencies and returns an `Arc<SimpleQueryDispatcher>`.

## Control Flow
`execute_query` builds a state machine, builds a logical plan, returns `Nil` for absent plans, then executes. `build_logical_plan` builds metadata, parses statements, rejects more than one statement and empty SQL, and delegates to `DefaultLogicalPlanner`. CSV setup maps S3 `FileHeaderInfo`: `USE` keeps headers, `IGNORE` treats the first row as headers but renames columns to `_1`, `_2`, and `NONE` sets no header and renames DataFusion `column_N` fields to `_N`. JSON uses the actual key extension, defaulting to `.json`. Parquet uses the custom table provider so scan ranges can prune row groups.

## State And Persistence Behavior
The dispatcher is request-scoped but can share parser/function/execution components. It builds per-query sessions and metadata providers. No durable query state is stored; state-machine transitions and metrics are in memory.

## Dependencies And Integration Points
It integrates API dispatcher traits, DataFusion listing CSV/JSON formats, parquet table provider, `MetadataProvider`, `BaseTableProvider`, parser, logical planner, execution factory, and S3 Select input serialization options.

## Risks And Edge Cases
The trait method `execute_logical_plan` calls the inherent method with the same name; resolution must remain to the inherent method to avoid recursion. CSV `FileHeaderInfo` must be present or the dispatcher returns not implemented. Only the first byte of comment, escape, quote, and one-byte delimiters is used by DataFusion; multi-byte field delimiters rely on `EcObjectStore` conversion. The default table-provider field is stored but a fresh `BaseTableProvider` is built in `build_table_handle_provider`, so injected provider state is not used there.

## Test Signals
Integration tests cover database creation, simple select, where, order, limit, staged state-machine execution, concurrent queries, JSON, parquet, and scan-range cases. Error tests cover syntax errors, multi-statement rejection, unsupported operations, empty SQL, and complex invalid queries.
