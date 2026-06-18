# sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/fixture.rs

## Purpose
This fixture module creates the common table and store used by index-scan benchmarks.

## Important APIs, Types, and Functions
`table_with_2_columns_and_one_index(rows)` returns `(index_id, Table, Store<RocksEngine>)`. It builds a table with primary-key `id` and indexed `foo`, allocates a fresh index id with `next_id`, and fills rows using `FixtureBuilder`.

## Control Flow
The helper constructs column metadata, creates the table, generates an `id` column as `0..n` and a random `foo` column, then writes rows into the test coprocessor store.

## State and Persistence Behavior
State lives in the returned in-memory/test store abstraction backed by `RocksEngine` fixtures. It is rebuilt per benchmark case.

## Dependencies and Integration Points
It depends on `test_coprocessor` table/column builders and common `FixtureBuilder`. `index_scan::mod` uses the returned table metadata to produce index ranges and selected column lists.

## Risks and Test Signals
The fixture assumes `foo` is indexed and `id` is the primary key. If table/index encoding changes, benchmark compilation or scan results through executor construction will reveal drift.
