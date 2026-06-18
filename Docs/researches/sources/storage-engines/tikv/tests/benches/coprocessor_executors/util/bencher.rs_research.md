# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/bencher.rs

## Purpose
This module defines reusable Criterion bench drivers for batch executors and DAG request handlers.

## Important APIs, Types, and Functions
`Bencher` is a trait with a generic `bench` method. `BatchNext1024Bencher` measures one `next_batch(1024)` call. `BatchNextAllBencher` repeatedly calls `next_batch(1024)` until the executor reports drained. `DagHandleBencher` measures `RequestHandler::handle_request`.

## Control Flow
Each driver uses `criterion::iter_batched_ref` to create fresh executor/handler state per sample, wraps work in `profiler::start/stop`, black-boxes results, and blocks async executor calls with `futures::executor::block_on`.

## State and Persistence Behavior
State is benchmark-local executor/handler state and generated profiler output files. No storage state is owned directly.

## Dependencies and Integration Points
It depends on `tidb_query_executors::BatchExecutor`, TiKV `RequestHandler`, Criterion, futures, and the optional profiler integration.

## Risks and Test Signals
The benchmark meaning depends on batch size 1024 and profiler overhead. `BatchNext1024Bencher` unwraps `is_drained`, so invalid executor results fail loudly. It is the common measurement layer for most coprocessor executor benchmarks.
