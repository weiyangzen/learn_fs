# sources/storage-engines/tikv/tests/benches/coprocessor_executors/hash_aggr/mod.rs

## Purpose
This module defines Criterion benchmark cases for TiKV batch hash aggregation executors. It measures COUNT/FIRST aggregates with different group-by expressions, cardinalities, and input types.

## Important APIs, Types, and Functions
Benchmark functions build `FixtureBuilder` inputs and TiDB expression protobufs with `ExprDefBuilder`. Cases include integer group-by with one group per row or two groups, scalar-function group-by, decimal group-by, multi-column group-by, and COUNT plus FIRST. `Input<M>` carries source row count and a boxed `HashAggrBencher`. `bench` registers sorted `BenchCase` values and expands rows/cases based on `TIKV_BENCH_LEVEL`.

## Control Flow
Each benchmark creates a synthetic batch fixture, builds group-by and aggregate expression lists, and delegates execution to `input.bencher.bench`. The default path benchmarks the batch bencher over 5000 rows; higher bench levels add smaller row counts and more cases.

## State and Persistence Behavior
State is temporary in-memory fixture columns and Criterion measurements. No durable store is used in this file.

## Dependencies and Integration Points
It depends on `hash_aggr::util`, common `BenchCase`/`FixtureBuilder`, `tidb_query_datatype`, `tipb`, and `tipb_helper`. It integrates into the top-level coprocessor executor benchmark runner through `hash_aggr::bench`.

## Risks and Test Signals
The benchmarks are sensitive to expression support in fast versus slow hash aggregation and to deterministic fixture generation. Compilation and Criterion output for all registered case/input names are the main signals; high bench levels exercise broader operator shapes.
