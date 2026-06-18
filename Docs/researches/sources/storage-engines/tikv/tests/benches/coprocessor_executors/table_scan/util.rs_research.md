# sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/util.rs

## Purpose
This utility module builds batch and DAG table-scan executors for scan benchmarks.

## Important APIs, Types, and Functions
`TableScanParam = ()`. `BatchTableScanExecutorBuilder<T>` implements `ScanExecutorBuilder` and returns a boxed batch executor. `TableScanExecutorDagBuilder<T>` builds protobuf table-scan descriptors for DAG handlers. Type aliases expose `BatchTableScanNext1024Bencher` and `TableScanDagBencher`.

## Control Flow
The batch builder creates `TikvStorage`, builds `BatchTableScanExecutor<ApiV1>`, performs a one-row warm-up to exclude scanner initialization, and returns the executor. The DAG builder delegates descriptor execution to `build_dag_handler`.

## State and Persistence Behavior
The module owns no durable state. Executors read from caller-provided fixture stores.

## Dependencies and Integration Points
It depends on API V1 query storage, futures `block_on`, `BatchTableScanExecutor`, common executor descriptors, and scan bencher traits.

## Risks and Test Signals
Constructor flags must track table scan executor signature changes. Warm-up behavior is intentional; removing it changes benchmark meaning.
