# sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/fixture.rs

## Purpose
This fixture module provides table/store shapes for integrated DAG executor benchmarks.

## Important APIs, Types, and Functions
It defines `table_with_int_column_two_groups`, `table_with_int_column_two_groups_ordered`, `table_with_int_column_n_groups`, and `table_with_3_int_columns_random`. The first three build `id` plus `foo` integer tables with sampled, ordered, or one-group-per-row values. The last builds `id`, `col1`, and `col2` random integer columns.

## Control Flow
Each helper constructs `test_coprocessor` table metadata, fills a `Store<RocksEngine>` through `FixtureBuilder`, and returns table/store pairs consumed by integrated benchmark cases.

## State and Persistence Behavior
Data is benchmark fixture state only. Ordered variants are used where stream aggregation requires grouped input.

## Dependencies and Integration Points
It depends on `test_coprocessor`, `tikv::storage::RocksEngine`, and common fixture building. `integrated/mod.rs` uses these helpers to build selection, aggregation, and top-N DAG pipelines.

## Risks and Test Signals
The fixture must keep column names/types aligned with expressions in integrated cases. Stream aggregation benchmarks rely on ordered grouping fixtures; using random fixtures there would change semantics and measured behavior.
