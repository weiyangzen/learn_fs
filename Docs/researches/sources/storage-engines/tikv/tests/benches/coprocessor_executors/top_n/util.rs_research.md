# sources/storage-engines/tikv/tests/benches/coprocessor_executors/top_n/util.rs

## Purpose
This utility module adapts `BatchTopNExecutor` to the shared benchmark interface.

## Important APIs, Types, and Functions
`TopNBencher<M>` defines benchmark execution with fixture builder, order-by expressions, sort directions, and limit. `BatchBencher` constructs `BatchTopNExecutor` from cloned fixture input and drains it through `BatchNextAllBencher`.

## Control Flow
Per iteration, it builds fresh source and TopN executor state, clones expression/order vectors, passes the limit, and drains all output batches.

## State and Persistence Behavior
The module is memory-only and owns no persistent state.

## Dependencies and Integration Points
It depends on `BatchTopNExecutor`, `EvalConfig`, Criterion black-boxing, and shared fixture/bencher utilities.

## Risks and Test Signals
`unwrap()` catches unsupported order-by definitions. Benchmark success across wide projection and high-limit cases validates TopN construction and batch draining.
