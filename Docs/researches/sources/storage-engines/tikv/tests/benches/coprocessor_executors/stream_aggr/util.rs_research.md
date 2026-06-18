# sources/storage-engines/tikv/tests/benches/coprocessor_executors/stream_aggr/util.rs

## Purpose
This utility module adapts `BatchStreamAggregationExecutor` to the benchmark harness.

## Important APIs, Types, and Functions
`StreamAggrBencher<M>` defines the bench interface. `BatchBencher` builds a batch stream aggregation executor with cloned fixture input, default evaluation config, group-by expressions, and aggregate expressions.

## Control Flow
The executor is constructed per iteration and drained with `BatchNextAllBencher`, measuring the full aggregation pipeline over the fixture source.

## State and Persistence Behavior
State is per-iteration memory. There is no storage engine persistence.

## Dependencies and Integration Points
It depends on `BatchStreamAggregationExecutor`, `EvalConfig`, `tikv::storage::Statistics`, and shared fixture/bencher utilities.

## Risks and Test Signals
`unwrap()` exposes unsupported descriptors. The stream executor's dependence on input ordering is handled by calling modules rather than this utility, so misuse by new cases is a risk.
