# sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/util.rs

## Purpose
This utility module builds batch and DAG index-scan executors for shared scan benchmarks.

## Important APIs, Types, and Functions
`IndexScanParam = bool` carries the unique-index flag. `BatchIndexScanExecutorBuilder<T>` implements `ScanExecutorBuilder` and returns a boxed `BatchExecutor<StorageStats = Statistics>`. `IndexScanExecutorDagBuilder<T>` implements `ScanExecutorDagHandlerBuilder` by creating a protobuf index-scan descriptor. Type aliases expose `BatchIndexScanNext1024Bencher` and `IndexScanDagBencher`.

## Control Flow
The batch builder constructs `TikvStorage` from the chosen store type, builds `BatchIndexScanExecutor<ApiV1>`, performs a one-row warm-up batch to pay scanner construction cost outside the measured loop, and returns the executor. The DAG builder delegates to `build_dag_handler`.

## State and Persistence Behavior
No persistent state is owned. The executor reads from the passed test store.

## Dependencies and Integration Points
It depends on API V1 query storage, futures `block_on`, `BatchIndexScanExecutor`, common executor descriptors, and scan bencher traits.

## Risks and Test Signals
Constructor parameters such as unique flag, index id `0`, and scan flags must match executor expectations. Compilation and successful warm-up are the main signals for interface drift.
