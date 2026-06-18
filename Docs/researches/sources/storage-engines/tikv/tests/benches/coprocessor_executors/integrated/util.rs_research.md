# sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/util.rs

## Purpose
This utility module abstracts integrated DAG benchmark execution over direct batch executors and request-handler DAG paths.

## Important APIs, Types, and Functions
`IntegratedBencher<M>` defines `name`, `bench`, and `box_clone`. `BatchBencher<T>` builds batch executors through `tidb_query_executors::runner::build_executors::<_, ApiV1>`. `DagBencher<T>` builds a full `RequestHandler` with `build_dag_handler`; its `batch` flag affects only the display tag through the shared helper path.

## Control Flow
Each Criterion iteration creates fresh executor state. Batch mode converts the fixture store into `TikvStorage`, passes executor descriptors and ranges to the runner, and drains with `BatchNextAllBencher`. DAG mode creates a handler and runs `handle_request` through `DagHandleBencher`.

## State and Persistence Behavior
The module keeps no durable state. Generic store type `T` selects memory or RocksDB-backed store behavior supplied by the caller.

## Dependencies and Integration Points
It depends on API V1 storage, `StubAccessor`, `EvalConfig`, `TikvStorage`, common bencher utilities, and store descriptors.

## Risks and Test Signals
Because it constructs real executor pipelines, `unwrap()` failures expose invalid descriptors or runner interface drift. Comparing batch and DAG benchmark names/results helps catch divergent execution paths.
