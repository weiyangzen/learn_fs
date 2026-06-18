# sources/storage-engines/tikv/tests/benches/coprocessor_executors/simple_aggr/util.rs

## Purpose
This utility module wraps `BatchSimpleAggregationExecutor` for Criterion benchmarks.

## Important APIs, Types, and Functions
`SimpleAggrBencher<M>` defines `name`, `bench`, and `box_clone`. `BatchBencher` constructs `BatchSimpleAggregationExecutor` from a cloned fixture source, default `EvalConfig`, and aggregate expression vector.

## Control Flow
Each iteration gets a fresh source executor and aggregation executor, then drains all batches through `BatchNextAllBencher`.

## State and Persistence Behavior
No persistent state; all data is memory fixture state.

## Dependencies and Integration Points
It depends on `tidb_query_executors::BatchSimpleAggregationExecutor`, `EvalConfig`, storage statistics, and common fixture/bencher utilities.

## Risks and Test Signals
Unsupported aggregate expressions panic through `unwrap()`. Successful runs validate that simple aggregation still consumes the shared fixture executor schema and batch interface.
