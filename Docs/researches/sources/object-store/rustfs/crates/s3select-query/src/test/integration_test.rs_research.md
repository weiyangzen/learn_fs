# sources/object-store/rustfs/crates/s3select-query/src/test/integration_test.rs

## Purpose
This file provides end-to-end tests for creating S3 Select DB instances and executing CSV, JSON, JSON-lines, and parquet queries, including scan ranges and concurrent execution.

## Important APIs, Types, And Functions
Fixture builders create CSV, JSON DOCUMENT, JSON LINES, and parquet `SelectObjectContentInput` values. Tests use `make_rustfsms`, `get_global_db`, `create_fresh_db`, `Query`, `Context`, and `QueryError`.

## Control Flow
Tests create test-mode databases, execute select queries, collect `QueryHandle` outputs into record batches, and assert success or expected row-count constraints. They also exercise staged state-machine planning and execution. Parquet scan-range tests mutate `request.scan_range` and verify row-group pruning outcomes.

## State And Persistence Behavior
All data comes from in-memory fixtures installed by `SessionCtxFactory` in test mode. Concurrent tests share the global component cache but create per-query contexts and sessions.

## Dependencies And Integration Points
The tests cover the full stack: crate root helpers, instance construction, dispatcher, parser, metadata provider, session fixture object stores, optimizer, physical planner, scheduler, output collection, `EcObjectStore` scan-range behavior in test mode, and parquet custom table provider.

## Risks And Edge Cases
Some aggregation tests accept failure due to lack of actual data, reducing strictness. Many tests assert success without checking exact values for CSV/JSON. Parquet row-count tests provide stronger correctness around scan-range pruning.

## Test Signals
Coverage includes DB creation, global/fresh DB creation, simple select, where, aggregation tolerance, invalid syntax, multi-statement errors, staged workflow, limit, order by, concurrent queries, JSON DOCUMENT, JSON LINES scan range, parquet simple select, tiny parquet scan range returning zero rows, full parquet scan range returning all rows, and CSV scan range returning rows.
