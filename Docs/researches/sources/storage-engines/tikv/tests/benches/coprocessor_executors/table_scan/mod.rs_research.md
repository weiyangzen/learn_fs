# sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/mod.rs

## Purpose
This module benchmarks table scan executor performance across projection patterns, row widths, missing columns, long values, and point ranges.

## Important APIs, Types, and Functions
Benchmark cases include primary-key-only scan, front/end/all datum projections from 100-column rows, long-column projections, absent/default column reads, absent columns in large rows, and many point ranges. `Input<M>` wraps a `ScanBencher<TableScanParam, M>`. `bench` configures memory batch, RocksDB DAG normal/batch, and additional high-level store combinations.

## Control Flow
Each case builds an appropriate fixture table/store, selects `ColumnInfo` values and ranges, then calls the selected scan bencher. Cases are sorted and registered under Criterion benchmark groups.

## State and Persistence Behavior
All data is benchmark fixture state. RocksDB-backed inputs may create temporary test engine state through common store helpers.

## Dependencies and Integration Points
It depends on table scan fixtures, `table_scan::util`, common `BenchCase`, scan benchers, and store descriptors. It is invoked by the top-level coprocessor executor benchmark entry point.

## Risks and Test Signals
The benchmark is a useful signal for scan decoder regressions: primary-key extraction, row datum decoding position, default-value handling, long varchars, and point-range overhead. Higher bench levels broaden store/execution modes.
