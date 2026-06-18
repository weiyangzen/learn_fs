# sources/storage-engines/tikv/tests/benches/coprocessor_executors/hash_aggr/util.rs

## Purpose
This utility module adapts hash aggregation executor construction to the shared benchmark harness.

## Important APIs, Types, and Functions
`HashAggrBencher<M>` defines `name`, `bench`, and `box_clone`. `BatchBencher` implements it by creating a fixture source, building a `tipb::Aggregation` metadata object, selecting `BatchFastHashAggregationExecutor` when `check_supported` succeeds, otherwise falling back to `BatchSlowHashAggregationExecutor`, and running through `BatchNextAllBencher`.

## Control Flow
For each Criterion iteration, the closure clones the fixture into a fresh `BatchFixtureExecutor`, clones expression vectors, creates an `EvalConfig`, instantiates the appropriate batch hash aggregation executor, and drains it in 1024-row batches.

## State and Persistence Behavior
All state is per-iteration memory. No external storage is touched.

## Dependencies and Integration Points
It depends on `criterion`, `tidb_query_executors` hash aggregation executors, `tidb_query_datatype::expr::EvalConfig`, `tikv::storage::Statistics`, and common fixture/bencher utilities.

## Risks and Test Signals
`unwrap()` makes unsupported construction fail fast. The fast/slow selection path is a key test signal: cases that stop satisfying fast aggregation constraints should still run through slow aggregation or fail clearly.
