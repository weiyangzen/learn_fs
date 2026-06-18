# sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/mod.rs

## Purpose
This module benchmarks index scan executor paths for retrieving either primary-key columns or indexed columns from a synthetic table.

## Important APIs, Types, and Functions
`bench_index_scan_primary_key` measures scanning an index while returning the primary key, modeling index lookup/double-read needs. `bench_index_scan_index` measures returning the indexed column itself. `Input<M>` wraps a `ScanBencher<IndexScanParam, M>`, and `bench` registers batch and DAG scan benchers for memory/RocksDB stores depending on bench level.

## Control Flow
Each case builds the fixture table/store, selects column metadata, creates an all-index key range, and calls the selected scan bencher with `unique = false`. Criterion groups are named by case and input display string.

## State and Persistence Behavior
Fixtures are generated per benchmark invocation. No persistent state is retained outside Criterion measurements and temporary RocksDB stores created by test utilities.

## Dependencies and Integration Points
It integrates with `index_scan::fixture`, `index_scan::util`, common `BenchCase`, `ScanBencher`, and store descriptors. The top-level coprocessor runner calls `index_scan::bench`.

## Risks and Test Signals
The benchmark only uses non-unique index mode. Higher bench levels add RocksDB direct batch scans and memory DAG variants, which are useful signals for store abstraction regressions.
