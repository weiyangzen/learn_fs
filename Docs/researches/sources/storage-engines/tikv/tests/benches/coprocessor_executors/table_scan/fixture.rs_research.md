# sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/fixture.rs

## Purpose
This module provides table/store fixtures for table scan benchmarks.

## Important APIs, Types, and Functions
`table_with_2_columns` builds `id` primary key plus `foo`. `table_with_multi_columns` builds `col0..colN` random integer columns. `table_with_missing_column` builds metadata for many columns but omits `col0` from stored rows so default-value behavior is measured. `table_with_long_column` builds `id`, `foo`, and a long varchar `bar`.

## Control Flow
Each helper constructs `test_coprocessor` table metadata and fills a `Store<RocksEngine>` via `FixtureBuilder` with deterministic row counts and column generators.

## State and Persistence Behavior
Fixture data is generated per benchmark. The returned store is test-only state.

## Dependencies and Integration Points
It depends on `test_coprocessor`, `RocksEngine`, and common fixture building. `table_scan/mod.rs` consumes these helpers to benchmark projection location, absent columns, long columns, and point ranges.

## Risks and Test Signals
Risks are column-name mismatches and unintended default handling changes. Compilation plus successful scan executor construction for missing/long column cases are the main signals.
