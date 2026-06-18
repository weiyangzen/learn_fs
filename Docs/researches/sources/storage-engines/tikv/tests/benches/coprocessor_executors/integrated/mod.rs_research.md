# sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/mod.rs

## Purpose
This module benchmarks multi-executor DAG pipelines that combine table scan, selection, aggregation, stream aggregation, hash aggregation, and top-N operators.

## Important APIs, Types, and Functions
It defines benchmark functions for `SELECT COUNT(1)`, `COUNT(column)`, plain selection, selection with low/medium/high selectivity, grouped counts with hash or stream aggregation, scalar group-by expressions, two-column group-by, selection plus group-by, three-column top-N, filtered top-N, and 50-column projection plus top-N. `Input<M>` combines row count and an `IntegratedBencher`.

## Control Flow
Every case builds table/store fixtures and a slice of protobuf executor descriptors using helpers from `executor_descriptor`. The selected bencher either constructs batch executors directly or wraps the protobuf DAG into a `RequestHandler`. `bench` expands row counts and bencher implementations by `bench_level`, registers a default set of representative cases, and adds broader cases at higher levels. Cases with limit 4000 skip work when row count is smaller.

## State and Persistence Behavior
State is per-benchmark fixture data and Criterion measurements. RocksDB-backed inputs use temporary test store state; memory inputs use fixture store state.

## Dependencies and Integration Points
It integrates the table-scan fixture module, local integrated fixtures, `integrated::util`, common executor descriptor builders, store descriptors, TiDB expression protobuf builders, and top-level coprocessor benchmark dispatch.

## Risks and Test Signals
Risks include expression column-index mismatches, stream aggregation requiring ordered input, and differences between batch executor and DAG handler behavior. Criterion compilation/runs across normal DAG, batch DAG, memory batch, and RocksDB batch inputs are the key regression signals.
